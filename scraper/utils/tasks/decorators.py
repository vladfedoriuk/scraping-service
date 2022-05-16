import functools
from typing import TypeVar, Type

from celery.utils.log import get_task_logger
from django.db import models

logger = get_task_logger(__name__)

ModelType = TypeVar("ModelType", bound=models.Model)


def get_instance_by_pk(
    model: Type[ModelType],
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(pk):
            try:
                instance = getattr(model, "_default_manager").get(pk=pk)
                return func(instance)
            except (model.DoesNotExist, model.MultipleObjectsReturned):
                logger.error(
                    f"Cannot retrieve an instance of {model.__qualname__!r} by {pk=!r}"
                )
                return

        return wrapper

    return decorator
