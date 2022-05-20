from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _

from scraper.models import (
    Topic,
    Resource,
    Integration,
    ScrapedData,
    ScraperConfiguration,
    IntegrationConsumption,
)
from scraper.utils.models.base import ExtendedActivatorModel


class IntegrationConsumptionInline(admin.StackedInline):
    model = IntegrationConsumption
    extra = 1


class IntegrationInline(admin.StackedInline):
    model = Integration
    extra = 1


class ResourceInline(admin.StackedInline):
    model = Resource
    extra = 1


class ScrapedDataInline(admin.StackedInline):
    extra = 0


class TopicAdmin(admin.ModelAdmin):
    inlines = [
        IntegrationInline,
        ResourceInline,
    ]

    list_display = (
        "id",
        "title",
        "created",
    )
    list_filter = (
        "created",
        "modified",
    )
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")
    search_fields = ["title", "description"]


class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "topic",
        "status",
        "priority",
        "created",
    )
    list_filter = (
        "status",
        "priority",
        "created",
        "modified",
        ("topic", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("topic",)
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")
    search_fields = ["title", "description", "topic__title", "topic__description"]


class IntegrationAdmin(admin.ModelAdmin):
    inlines = [
        IntegrationConsumptionInline,
    ]

    list_display = (
        "id",
        "title",
        "status",
        "created",
    )
    list_filter = (
        "status",
        "created",
        "modified",
        ("topic", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("topic",)
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")
    search_fields = ["title", "description", "topic__title", "topic__description"]


class ScrapedDataAdmin(admin.ModelAdmin):
    inlines = [
        IntegrationConsumptionInline,
    ]
    list_display = (
        "id",
        "resource",
        "created",
    )
    list_filter = (
        "created",
        "modified",
        ("resource", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("resource",)
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    search_fields = ["resource__title", "resource__description"]


class ScraperConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "scraper_name",
        "resource",
        "created",
        "is_active",
    )
    list_filter = (
        "created",
        "modified",
        "scraper_name",
        ("resource", admin.RelatedOnlyFieldListFilter),
    )
    list_select_related = ("resource",)
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    search_fields = ["resource__title", "resource__description", "scraper_name"]

    actions = ["start_scraping", "stop_scraping"]

    @admin.action(description=_("Start the related scraping algorithms"))
    def start_scraping(self, request, queryset):
        from scraper.tasks import scraping_dispatcher
        queryset.update(status=ScraperConfiguration.ACTIVE_STATUS)
        resources_pk = queryset.values_list("resource__pk", flat=True)
        for resource_pk in resources_pk:
            scraping_dispatcher.apply_async(args=(resource_pk,))
        self.message_user(
            request,
            ngettext(
                _("%d scraper algorithm has been successfully started."),
                _("%d scraper algorithms have been successfully started."),
                len(resources_pk),
            )
            % len(resources_pk),
            messages.SUCCESS,
        )

    @admin.action(description=_("Halt the related scraping algorithms"))
    def stop_scraping(self, request, queryset):
        num_inactivated = queryset.update(status=ExtendedActivatorModel.INACTIVE_STATUS)
        self.message_user(
            request,
            ngettext(
                _("%d scraper algorithm has been successfully inactivated."),
                _("%d scraper algorithms have been successfully inactivated."),
                num_inactivated,
            )
            % num_inactivated,
            messages.SUCCESS,
        )


admin.site.register(ScraperConfiguration, ScraperConfigurationAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Integration, IntegrationAdmin)
admin.site.register(ScrapedData, ScrapedDataAdmin)
