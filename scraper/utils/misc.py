import functools
from typing import Type, Optional

from celery.utils.log import get_task_logger

from django.db import models

from scraper.models import ScrapedData


def get_instance_by_pk(
    model: Type[models.Model],
):
    logger = get_task_logger(__name__)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(pk):
            try:
                instance = model._default_manager.get(pk=pk)
                return func(instance)
            except (model.DoesNotExist, model.MultipleObjectsReturned):
                logger.error(
                    f"Cannot retrieve an instance of {model.__qualname__!r} by {pk=!r}"
                )
                return

        return wrapper

    return decorator


def get_scraped_data_by_pk(pk: int) -> Optional[ScrapedData]:
    try:
        return (
            ScrapedData.objects.all()
            .prefetch_related("resource__topic__integrations")
            .get(pk=pk)
        )
    except (ScrapedData.DoesNotExist, ScrapedData.MultipleObjectsReturned):
        return None
