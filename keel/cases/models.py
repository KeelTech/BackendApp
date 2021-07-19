import uuid
from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.plans.models import Plan
from keel.authentication.models import User

class Case(TimeStampedModel, SoftDeleteModel):

    BOOKED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELLED = 4

    CASES_TYPE_CHOICES = (
        (BOOKED, 'BOOKED'),
        (IN_PROGRESS, 'IN_PROGRESS'),
        (COMPLETED, 'COMPLETED'),
        (CANCELLED, 'CANCELLED'),
    )

    case_id = models.CharField(max_length=255, primary_key=True, default=None, blank=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases', default=None, null=True, blank=True)
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases', default=None, null=True, blank=True)
    account_manager_id = models.IntegerField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=CASES_TYPE_CHOICES, verbose_name="case_status", default=BOOKED, null=True, blank=True)
    is_active = models.BooleanField(verbose_name= 'Active', default=True)
    ref_id = models.ForeignKey('self',null=True, blank=True, on_delete=models.deletion.DO_NOTHING)
    plan = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING, related_name='plans_cases', default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.case_id = uuid.uuid4()
        super().save(*args, **kwargs)