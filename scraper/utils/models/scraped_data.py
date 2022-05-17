from typing import Optional

from scraper.models import ScrapedData


def get_scraped_data_by_pk(pk: int) -> Optional[ScrapedData]:
    try:
        return (
            ScrapedData.objects.all()
            .prefetch_related("resource__topic__integrations")
            .get(pk=pk)
        )
    except (ScrapedData.DoesNotExist, ScrapedData.MultipleObjectsReturned):
        return None
