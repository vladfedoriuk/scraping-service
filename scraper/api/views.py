from rest_flex_fields import is_expanded
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.viewsets import ReadOnlyModelViewSet

from scraper.api.serializers import ScrapedDataSerializer
from scraper.models import ScrapedData
from scraper.utils.models.misc import get_queryset


class ScrapedDataViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    queryset = get_queryset(ScrapedData)
    serializer_class = ScrapedDataSerializer

    def get_queryset(self):
        queryset = get_queryset(ScrapedData)
        if is_expanded(self.request, "resource"):
            queryset = queryset.select_related("resource")
        if is_expanded(self.request, "topic"):
            queryset = queryset.select_related("resource__topic")
        return queryset
