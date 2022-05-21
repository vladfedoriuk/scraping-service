from typing import Optional

from django.db.models import QuerySet

from scraper.models import ScrapedData
from scraper.utils.models.misc import get_queryset, get_default_manager


def get_scraped_data_by_pk(pk: int) -> Optional[ScrapedData]:
    qs = get_queryset(ScrapedData)
    try:
        return (
            get_default_manager(ScrapedData)
            .select_related("resource")
            .select_related("resource__topic")
            .prefetch_related("resource__topic__integrations")
            .get(pk=pk)
        )
    except (qs.model.DoesNotExist, qs.model.MultipleObjectsReturned):
        return None


def get_scraped_data_by_pk_list(pk_list: list[int]) -> Optional[QuerySet[ScrapedData]]:
    return (
        get_default_manager(ScrapedData)
        .select_related("resource__topic")
        .prefetch_related("resource__topic__integrations")
        .filter(pk__in=pk_list)
    ).distinct()
