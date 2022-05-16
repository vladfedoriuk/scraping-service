from typing import Optional, TypeVar, Union, Type, cast

from django.db import models
from django.db.models import QuerySet, Manager

from scraper.models import ScrapedData

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


def get_scraped_data_by_pk(pk: int) -> Optional[ScrapedData]:
    try:
        return (
            ScrapedData.objects.all()
            .prefetch_related("resource__topic__integrations")
            .get(pk=pk)
        )
    except (ScrapedData.DoesNotExist, ScrapedData.MultipleObjectsReturned):
        return None