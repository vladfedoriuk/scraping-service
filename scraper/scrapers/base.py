import contextlib
import dataclasses
import functools
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional, Union, Sequence

from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils.functional import classproperty, cached_property

from scraper.utils.models.misc import get_object_or_none, get_default_manager

from typing import TYPE_CHECKING

# https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
if TYPE_CHECKING:
    from scraper.models import ScrapedData, ScraperConfiguration, Resource

__all__ = ("Scraper", "ScrapeResult")


logger = get_task_logger(__name__)


@dataclasses.dataclass(frozen=True)
class ScrapeResult:
    data: Union["ScrapedData", Sequence["ScrapedData"]]
    state: dict

    @cached_property
    def is_empty(self) -> bool:
        return not self.data if isinstance(self.data, Sequence) else self.data.is_empty


class Scraper(ABC):
    scrape_data_countdown: timedelta = timedelta(minutes=10)
    app_name = "scraper"

    @staticmethod
    def ensure_configuration(is_atomic: bool = False):
        def decorator(method):
            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                context = (
                    transaction.atomic() if is_atomic else contextlib.nullcontext()
                )
                with context:
                    self.__reload_configuration_if_none()
                    self.__check_configuration_has_been_loaded()
                    return method(self, *args, **kwargs)

            return wrapper

        return decorator

    @classproperty
    def scraper_name(cls) -> str:
        return f"{cls.app_name}:{cls.__qualname__.lower()}"

    def __init_subclass__(cls, **kwargs):
        from scraper.scrapers.registry import add_to_registry

        add_to_registry(cls)
        super().__init_subclass__(**kwargs)

    def __reload_configuration(self) -> Optional["ScraperConfiguration"]:
        from scraper.models import ScraperConfiguration

        self.__configuration = get_object_or_none(
            ScraperConfiguration, scraper_name=self.scraper_name
        )
        return self.__configuration

    def __reload_configuration_if_none(self):
        if self.__configuration is None:
            self.__reload_configuration()

    def __check_configuration_has_been_loaded(self):
        if self.__configuration is None:
            raise RuntimeError(
                f"Cannot read the configuration for {self.scraper_name=}"
            )

    def __init__(self):
        from scraper.models import ScraperConfiguration

        self.__configuration: Optional[ScraperConfiguration] = None

    def build_scraped_data(
        self, data: Union[dict, Sequence[dict]]
    ) -> Union["ScrapedData", Sequence["ScrapedData"]]:
        from scraper.models import ScrapedData

        manager = get_default_manager(ScrapedData)
        if isinstance(data, Sequence):
            manager.bulk_create(
                scraped_data := [
                    ScrapedData(resource=self.resource, data=data_point)
                    for data_point in data
                ]
            )
        else:
            scraped_data = manager.create(resource=self.resource, data=data)
        return scraped_data

    @property
    @ensure_configuration()
    def state(self) -> Optional[dict]:
        return self.__configuration.state

    @state.setter
    @ensure_configuration(is_atomic=True)
    def state(self, state_data):
        self.__configuration.state = state_data
        self.__configuration.save(update_fields=("state",))

    @property
    @ensure_configuration()
    def resource(self) -> Optional["Resource"]:
        return self.__configuration.resource

    @property
    def is_active(self) -> bool:
        return self.resource.is_active and self.__configuration.is_active

    @ensure_configuration(is_atomic=True)
    def deactivate(self):
        from scraper.models import ScraperConfiguration

        self.__configuration.status = ScraperConfiguration.INACTIVE_STATUS
        self.__configuration.save(update_fields=("status",))

    @abstractmethod
    def scrape(self) -> ScrapeResult:
        ...

    def step(self) -> ScrapeResult:
        from scraper.models import ScraperConfiguration

        self.__reload_configuration()
        pk = self.__configuration.pk
        log_prefix = f"[{ScraperConfiguration.__qualname__} with {pk=}] "
        logger.info(f"Reloaded the configuration for {self.__class__.__qualname__}")
        logger.info(f"{log_prefix}Verifying the resource is active.")
        if not self.resource.is_active:
            raise RuntimeError(f"Cannot start scraping inactive {self.resource=}")
        logger.info(f"{log_prefix}Verifying the scraper is active.")
        if not self.is_active:
            raise RuntimeError(
                f"An attempt to start an inactive "
                f"scraping algorithm with {self.scraper_name=}"
            )
        logger.info(f"{log_prefix}Performing a scraping step.")
        scrape_result = self.scrape()
        logger.info(f"{log_prefix}Updating a scraper state.")
        self.state = scrape_result.state
        if scrape_result.is_empty:
            logger.info(f"{log_prefix}Deactivating a scraper state.")
            self.deactivate()
        return scrape_result
