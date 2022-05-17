from functools import partial

from celery import shared_task, Task
from celery.utils.log import get_task_logger

from scraper.models import ScrapedData, Resource
from scraper.scrapers import get_from_registry
from scraper.utils.client.client import HttpClient
from scraper.utils.models.resource import get_resource_by_pk
from scraper.utils.tasks.hooks import add_consumer
from scraper.utils.models.scraped_data import get_scraped_data_by_pk
from scraper.utils.tasks.base import TaskWithRetryMixin, TransactionAwareTaskMixin

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
        )
        return

    client = HttpClient()
    add_consumer_hook = partial(add_consumer, scraped_data)
    for integration in scraped_data.resource.topic.integrations:
        if not scraped_data.consumers.filter(pk=integration.pk).exists():
            client.post(
                url=integration.hook_url,
                request_kwargs={
                    "json": scraped_data.data,
                },
                client_kwargs={
                    "event_hooks": {
                        "response": [add_consumer_hook(integration)],
                    }
                },
            )


@shared_task(base=ScrapingDispatcherTask)
def scraping_dispatcher(resource_pk: int):
    resource = get_resource_by_pk(pk=resource_pk)
    if resource is None:
        logger.error(f"Cannot retrieve an instance of {Resource!r} by {resource_pk=!r}")
        return

    scraper_names = [
        config.scraper_name for config in getattr(resource, "scraper_configs")
    ]
    for scraper_name in scraper_names:
        scrape_data.apply_async(args=(scraper_name,))


@shared_task(base=ScrapingTask)
def scrape_data(scraper_name: str):
    scraper_cls = get_from_registry(scraper_name)
    scraper = scraper_cls()
    data = scraper.step()
