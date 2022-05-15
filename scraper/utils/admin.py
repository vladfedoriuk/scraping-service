from typing import cast

from django.contrib.admin import ModelAdmin


class ReadOnlyAdminMixin:
    """Disables all editing capabilities."""

    change_form_template = "admin/view.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields = tuple(
            field.name
            for field in getattr(cast(ModelAdmin, self).model, "_meta").get_fields()
        )

    def get_actions(self, request):
        actions = cast(ModelAdmin, super()).get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        pass

    def save_related(self, request, form, formsets, change):
        pass
