from typing import Optional

from scraper.models import Resource
from scraper.utils.models.misc import get_default_manager


def get_resource_by_pk(pk: int) -> Optional[Resource]:
    try:
        return (
            get_default_manager(Resource).prefetch_related("scraper_configs").get(pk=pk)
        )
    except (Resource.DoesNotExist, Resource.MultipleObjectsReturned):
        return None
