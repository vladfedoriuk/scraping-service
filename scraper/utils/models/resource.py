from typing import Optional

from scraper.models import Resource


def get_resource_by_pk(pk: int) -> Optional[Resource]:
    try:
        return Resource.objects.all().prefetch_related("scraper_configs").get(pk=pk)
    except (Resource.DoesNotExist, Resource.MultipleObjectsReturned):
        return None
