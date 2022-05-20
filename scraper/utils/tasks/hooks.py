import logging
from collections.abc import Sequence

import httpx

from scraper.models import ScrapedData, Integration, IntegrationConsumption


def add_consumer(scraped_data: ScrapedData, integration: Integration):

    def response_hook(logger: logging.Logger, response: httpx.Response):
        if response.is_success:
            logger.info(
                f"Sent a {ScrapedData!r} instance with pk={scraped_data.pk}"
                f" to integration with pk={integration.pk}"
            )
            scraped_data.consumers.add(integration)

    return response_hook


def add_consumers(scraped_data_batch: Sequence[ScrapedData], integration: Integration):

    scraped_data_pk_list = [data.pk for data in scraped_data_batch]

    def response_hook(logger: logging.Logger, response: httpx.Response):
        if response.is_success:
            logger.info(
                f"Sent a batch of {ScrapedData!r} instances "
                f"with pk={scraped_data_pk_list} "
                f"to integration with pk={integration.pk}"
            )
            IntegrationConsumption.objects.create_batch(
                [
                    IntegrationConsumption(integration=integration, scraped_data=data)
                    for data in scraped_data_batch
                ]
            )

    return response_hook
