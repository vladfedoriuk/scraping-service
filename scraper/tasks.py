from collections.abc import Iterable
from functools import partial

from celery import shared_task, Task
from celery.utils.log import get_task_logger

from scraper.api.serializers import ScrapedDataSerializer
from scraper.models import ScrapedData, Resource
from scraper.scrapers import get_from_registry, Scraper, ScrapeResult
from scraper.utils.client.client import HttpClient
from scraper.utils.decorators.misc import with_logger
from scraper.utils.models.resource import get_resource_by_pk
from scraper.utils.tasks.hooks import add_consumer, add_consumers
from scraper.utils.models.scraped_data import (
    get_scraped_data_by_pk,
    get_scraped_data_by_pk_list,
)
from scraper.utils.tasks.mixins import TaskWithRetryMixin, TransactionAwareTaskMixin

logger = get_task_logger(__name__)


class ScrapingDispatcherTask(Task, TaskWithRetryMixin):
    pass


class ScrapingTask(Task, TaskWithRetryMixin):
    autoretry_for = (RuntimeError, AssertionError)


class SendScrapedDataTask(Task, TaskWithRetryMixin, TransactionAwareTaskMixin):
    pass


@shared_task(base=SendScrapedDataTask)
def send_data(scraped_data_pk: int):

    scraped_data = get_scraped_data_by_pk(pk=scraped_data_pk)
    if scraped_data is None:
        logger.error(
            f"Cannot retrieve an instance of {ScrapedData!r} by {scraped_data_pk=!r}"
            f"Aborting sending data."
        )
        return

    if not scraped_data.data:
        logger.error(
            f"The provided {ScrapedData!r} with {scraped_data_pk=} has no data to send"
            f"Aborting sending data."
        )
        return

    client = HttpClient()
    add_consumer_hook = partial(add_consumer, scraped_data)
    for integration in scraped_data.resource.topic.integrations.all():
        client.post(
            url=integration.hook_url,
            request_kwargs={
                "json": ScrapedDataSerializer(instance=scraped_data).data,
            },
            client_kwargs={
                "event_hooks": {
                    "response": [with_logger(logger)(add_consumer_hook(integration))],
                }
            },
        )


@shared_task(base=SendScrapedDataTask)
def send_batched_data(scraped_data_pk_list: list[int]):

    scraped_data_batch = get_scraped_data_by_pk_list(pk_list=scraped_data_pk_list)
    if not scraped_data_batch:
        logger.error(
            f"The queryset for {scraped_data_pk_list=} is empty."
            f"Aborting sending data"
        )
        return

    client = HttpClient()
    add_consumer_hook = partial(add_consumers, scraped_data_batch)
    integrations = next(iter(scraped_data_batch)).resource.topic.integrations.all()
    for integration in integrations:
        client.post(
            url=integration.hook_url,
            request_kwargs={
                "json": ScrapedDataSerializer(scraped_data_batch, many=True).data,
            },
            client_kwargs={
                "event_hooks": {
                    "response": [with_logger(logger)(add_consumer_hook(integration))],
                }
            },
        )


@shared_task(base=ScrapingDispatcherTask)
def scraping_dispatcher(resource_pk: int):
    resource: Resource = get_resource_by_pk(pk=resource_pk)
    if resource is None:
        logger.error(f"Cannot retrieve an instance of {Resource!r} by {resource_pk=!r}")
        return

    if not resource.is_active:
        logger.error(
            f"The {Resource!r} with {resource_pk=!r} is inactive. "
            f"Aborted scraping dispatching."
        )
        return

    scraper_names = (
        getattr(resource, "scraper_configs")
        .all()
        .values_list("scraper_name", flat=True)
    )
    for scraper_name in scraper_names:
        scrape_data.apply_async(args=(scraper_name,))


@shared_task(base=ScrapingTask)
def scrape_data(scraper_name: str):
    scraper_cls = get_from_registry(scraper_name)
    scraper: Scraper = scraper_cls()
    if not scraper.is_active:
        logger.error(
            f"The {Scraper!r} with {scraper_name=!r} is inactive. "
            f"Aborted scraping process."
        )
        return

    scraped_result: ScrapeResult = scraper.step()

    if scraped_result.is_empty:
        logger.error(
            f"The {Scraper!r} with {scraper_name=!r} returned empty data. "
            f"Halting scraping process."
        )
        return

    scraped_data = scraped_result.data
    if isinstance(scraped_data, Iterable):
        send_batched_data.apply_async(args=([data.pk for data in scraped_data],))
    else:
        send_data.apply_async(args=(scraped_data.pk,))
    scrape_data.apply_async(
        args=(scraper_name,), countdown=scraper.scrape_data_countdown.seconds
    )
