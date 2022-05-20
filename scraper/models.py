from django.db import models
from django.db.models import URLField
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.models import (
    TitleSlugDescriptionModel,
    TimeStampedModel,
)
from django.utils.translation import gettext_lazy as _

from scraper.scrapers.registry import scraper_choices
from scraper.utils.models.base import ExtendedActivatorModel


class Topic(
    TimeStampedModel,
    TitleSlugDescriptionModel,
):
    pass


class Resource(
    TimeStampedModel,
    ExtendedActivatorModel,
    TitleSlugDescriptionModel,
):
    class PriorityChoices(models.IntegerChoices):
        LOW = 0, _("Low")
        MODERATE = 1, _("Moderate")
        HIGH = 2, _("High")

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        verbose_name=_("topic"),
        help_text=_("The related topic."),
        related_name="resources",
        related_query_name="resource",
    )
    url = URLField(
        verbose_name=_("resource url"),
        help_text=_("This url will be used to start scraping process."),
    )
    priority = models.SmallIntegerField(
        choices=PriorityChoices.choices,
        default=PriorityChoices.LOW,
        verbose_name=_("resource priority"),
        help_text=_(
            "The priorities define the order in which the resources will be getting scrapped."
        ),
    )


class Integration(
    TimeStampedModel,
    ExtendedActivatorModel,
    TitleSlugDescriptionModel,
):
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        verbose_name=_("topic"),
        help_text=_("The related topic."),
        related_name="integrations",
        related_query_name="integration",
    )
    hook_url = URLField(
        verbose_name=_("resource url"),
        help_text=_("This url will be used to post scrapped data."),
    )


class IntegrationConsumption(models.Model):
    created = CreationDateTimeField(_("created"))
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        verbose_name=_("integration"),
        related_name="data_consumptions",
        related_query_name="data_consumption",
    )
    scrapped_data = models.ForeignKey(
        "scraper.ScrapedData",
        on_delete=models.CASCADE,
        verbose_name=_("scrapped data"),
        related_name="integration_consumptions",
        related_query_name="integration_consumption",
    )


class ScrapedData(TimeStampedModel):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        verbose_name=_("resource"),
        help_text=_("The related resource."),
        related_name="scrapped_data",
    )
    consumers = models.ManyToManyField(
        Integration,
        through=IntegrationConsumption,
        through_fields=("scrapped_data", "integration"),
        verbose_name=_("consumers"),
        help_text=_("The integrations which have already consumed this data."),
        related_name="consumed_data",
    )
    data = models.JSONField(
        verbose_name=_("data"), help_text=_("The scrapped data."), default=dict
    )

    class Meta:
        verbose_name = _("Scrapped Data")
        verbose_name_plural = verbose_name


class ScraperConfiguration(
    TimeStampedModel,
    ExtendedActivatorModel,
):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        verbose_name=_("resource"),
        help_text=_("The related resource."),
        related_name="scraper_configs",
        related_query_name="scraper_config",
    )
    state = models.JSONField(
        verbose_name=_("state"),
        help_text=_("The scrapped data."),
        default=dict,
        blank=True,
    )
    scraper_name = models.CharField(
        _("A scraper name"),
        help_text=_("A name of scraping algorithm to use."),
        max_length=128,
        unique=True,
        choices=scraper_choices(),
    )
