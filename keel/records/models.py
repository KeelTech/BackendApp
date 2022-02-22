from django.contrib.auth import get_user_model
from django.db import models
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.plans.models import Plan


User = get_user_model()


class SalesUser(TimeStampedModel, SoftDeleteModel):
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="sales_user_created_by",
        default=None,
        blank=True,
        null=True,
    )
    email = models.EmailField(max_length=255)
    agent = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="sales_user_agent",
        default=None,
        blank=True,
        null=True,
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.DO_NOTHING, default=None, blank=True, null=True
    )

    def __str__(self) -> str:
        return str(self.email)
