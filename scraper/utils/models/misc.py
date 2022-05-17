from typing import TypeVar, Union, Type, cast, Optional

from django.db import models
from django.db.models import QuerySet, Manager

ModelType = TypeVar("ModelType", bound=models.Model)


def get_queryset(resource: Union[Type[ModelType], QuerySet, Manager]) -> QuerySet:
    if hasattr(resource, "_default_manager"):
        queryset: QuerySet = getattr(resource, "_default_manager").all()
        return queryset
    if hasattr(resource, "get"):
        return cast(QuerySet, resource)
    raise TypeError(
        f"The resource must be a Model, Manager, or a QuerySet. Got: {resource}"
    )


def get_object_or_none(
    resource: Union[Type[ModelType], QuerySet, Manager], *args, **kwargs
) -> Optional[ModelType]:
    queryset = get_queryset(resource)
    try:
        return queryset.get(*args, **kwargs)
    except (queryset.model.DoesNotExist, queryset.model.MultipleObjectsReturned):
        return None
