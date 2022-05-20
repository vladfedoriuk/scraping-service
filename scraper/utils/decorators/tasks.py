import functools
from typing import TypeVar, Type

from celery.utils.log import get_task_logger
from django.db import models

from scraper.utils.models.misc import get_queryset

logger = get_task_logger(__name__)

ModelType = TypeVar("ModelType", bound=models.Model)


def accept_model(
    model: Type[ModelType],
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(pk):
            try:
                instance = get_queryset(model).get(pk=pk)
                return func(instance)
            except (model.DoesNotExist, model.MultipleObjectsReturned):
                logger.error(
                    f"Cannot retrieve an instance of {model.__qualname__!r} by {pk=!r}"
                )
                return

        return wrapper

    return decorator
