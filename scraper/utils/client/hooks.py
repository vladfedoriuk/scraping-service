import logging

import httpx
from celery.utils.log import get_task_logger

from scraper.models import ScrapedData, Integration


def log_request(request: httpx.Request):
    logger = logging.getLogger("django")
    logger.info(
        f"Request event hook: {request.method} {request.url} - Waiting for response"
    )


def log_response(response: httpx.Response):
    logger = logging.getLogger("django")
    request = response.request
    logger.info(
        f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
    )


def raise_on_4xx_5xx(response: httpx.Response):
    response.raise_for_status()


def add_consumer(scraped_data: ScrapedData, integration: Integration):

    logger = get_task_logger(__name__)

    def response_hook(response: httpx.Response):
        if response is not None and response.is_success:
            logger.info(
                f"Sent a {ScrapedData!r} instance with pk={scraped_data.pk}"
                f" to integration with pk={integration.pk}"
            )
            scraped_data.consumers.add(integration)

    return response_hook
