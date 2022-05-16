from functools import partial

from celery import shared_task, Task
from celery.utils.log import get_task_logger

from scraper.models import ScrapedData
from scraper.utils.client.client import HttpClient
from scraper.utils.client.hooks import add_consumer
from scraper.utils.misc import get_scraped_data_by_pk
from scraper.utils.tasks import TaskWithRetryMixin, TransactionAwareTaskMixin

logger = get_task_logger(__name__)


class ScrapingTask(Task, TaskWithRetryMixin):
    pass


class SendScrapedDataTask(Task, TaskWithRetryMixin, TransactionAwareTaskMixin):
    pass


@shared_task(base=ScrapingTask)
def scrape():
    pass


@shared_task(base=SendScrapedDataTask)
def send_data(pk: int):

    scraped_data = get_scraped_data_by_pk(pk=pk)
    if scraped_data is None:
        logger.error(f"Cannot retrieve an instance of {ScrapedData!r} by {pk=!r}")
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
                        "response": [add_consumer_hook],
                    }
                },
            )
