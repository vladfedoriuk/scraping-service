import dataclasses
from abc import ABC, abstractmethod
from typing import Optional, Union, Sequence

from django.db import transaction
from django.utils.functional import classproperty, cached_property

from typing import TYPE_CHECKING

# https://adamj.eu/tech/2021/05/13/python-type-hints-how-to-fix-circular-imports/
if TYPE_CHECKING:
    from scraper.models import ScrapedData, ScraperConfiguration, Resource

__all__ = ("Scraper",)

from scraper.utils.models.misc import get_object_or_none, get_default_manager


@dataclasses.dataclass(frozen=True)
class ScrapeResult:
    data: Union["ScrapedData", Sequence["ScrapedData"]]
    state: dict

    @cached_property
    def is_empty(self) -> bool:
        return self.data.is_empty


class Scraper(ABC):
    app_name = "scraper"

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

        if isinstance(data, Sequence):
            get_default_manager(ScrapedData).bulk_create(
                scraped_data := [
                    ScrapedData(resource=self.resource, data=data_point)
                    for data_point in data
                ]
            )
        else:
            scraped_data = get_default_manager(ScrapedData).create(
                resource=self.resource, data=data
            )
        return scraped_data

    @property
    def state(self) -> Optional[dict]:
        self.__reload_configuration_if_none()
        self.__check_configuration_has_been_loaded()
        return self.__configuration.state

    @state.setter
    def state(self, state_data):
        with transaction.atomic():
            self.__reload_configuration_if_none()
            self.__check_configuration_has_been_loaded()
            self.__configuration.state = state_data
            self.__configuration.save(update_fields=("state",))

    @property
    def resource(self) -> Optional["Resource"]:
        self.__reload_configuration_if_none()
        self.__check_configuration_has_been_loaded()
        return self.__configuration.resource

    @property
    def is_active(self) -> bool:
        return self.resource.is_active and self.__configuration.is_active

    def deactivate(self):
        from scraper.models import ScraperConfiguration

        with transaction.atomic():
            self.__reload_configuration_if_none()
            self.__check_configuration_has_been_loaded()
            self.__configuration.status = ScraperConfiguration.INACTIVE_STATUS
            self.__configuration.save(update_fields=("status",))

    @abstractmethod
    def scrape(self) -> ScrapeResult:
        ...

    def step(self) -> Union["ScrapedData", Sequence["ScrapedData"]]:
        self.__reload_configuration()
        if not self.resource.is_active:
            raise RuntimeError(f"Cannot start scraping inactive {self.resource=}")
        if not self.is_active:
            raise RuntimeError(
                f"An attempt to start an inactive "
                f"scraping algorithm with {self.scraper_name=}"
            )
        scrape_result = self.scrape()
        self.state = scrape_result.state
        if scrape_result.is_empty:
            self.deactivate()
        return scrape_result.data
