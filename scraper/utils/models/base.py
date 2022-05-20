from django.contrib import admin
from django_extensions.db.models import ActivatorModel


class ExtendedActivatorModel(ActivatorModel):
    @property
    @admin.display(
        description="Is active",
        boolean=True,
    )
    def is_active(self) -> bool:
        return self.status == ActivatorModel.ACTIVE_STATUS

    class Meta:
        abstract = True
