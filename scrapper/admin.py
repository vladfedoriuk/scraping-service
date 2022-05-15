from operator import attrgetter

from django.contrib import admin

from scrapper.models import Topic, Resource, Integration, ScrappedData
from scrapper.utils.admin import ReadOnlyAdminMixin


class IntegrationInline(admin.StackedInline):
    model = Integration
    extra = 1


class ResourceInline(admin.StackedInline):
    model = Resource
    extra = 1


class ScrappedDataInline(ReadOnlyAdminMixin, admin.StackedInline):
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


class ScrappedDataAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
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

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Topic, TopicAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Integration, IntegrationAdmin)
admin.site.register(ScrappedData, ScrappedDataAdmin)
