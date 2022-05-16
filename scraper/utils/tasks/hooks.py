import httpx
from celery.utils.log import get_task_logger

from scraper.models import ScrapedData, Integration


def add_consumer(scraped_data: ScrapedData, integration: Integration):

    logger = get_task_logger(__name__)

    def response_hook(response: httpx.Response):
        if response.is_success:
            logger.info(
                f"Sent a {ScrapedData!r} instance with pk={scraped_data.pk}"
                f" to integration with pk={integration.pk}"
            )
            scraped_data.consumers.add(integration)

    return response_hook
