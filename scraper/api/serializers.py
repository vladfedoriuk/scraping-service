from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.serializers import ModelSerializer

from scraper.models import Topic, Resource, ScrapedData


class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class ResourceSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"

    expandable_fields = {"topic": TopicSerializer}


class ScrapedDataSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ScrapedData
        exclude = ("consumers",)
        expandable_fields = {"resource": ResourceSerializer}
