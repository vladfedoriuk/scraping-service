from typing import Optional

from django.db.models import QuerySet

from scraper.models import ScrapedData
from scraper.utils.models.misc import get_queryset


def get_scraped_data_by_pk(pk: int) -> Optional[ScrapedData]:
    try:
        return (
            get_queryset(ScrapedData)
            .prefetch_related("resource__topic__integrations")
            .get(pk=pk)
        )
    except (ScrapedData.DoesNotExist, ScrapedData.MultipleObjectsReturned):
        return None


def get_scraped_data_by_pk_list(pk_list: list[int]) -> Optional[QuerySet[ScrapedData]]:
    return (
        get_queryset(ScrapedData)
        .prefetch_related("resource__topic__integrations")
        .filter(pk__in=pk_list)
    ).distinct()
