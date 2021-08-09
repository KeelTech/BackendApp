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

    case_id = models.CharField(max_length=255, primary_key=True)
    display_id = models.CharField(max_length=5, default=None, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases')
    account_manager_id = models.IntegerField(null=True, blank=True, default=None)
    status = models.PositiveSmallIntegerField(choices=CASES_TYPE_CHOICES, verbose_name="case_status", default=BOOKED)
    is_active = models.BooleanField(verbose_name= 'Active', default=True)
    ref_id = models.ForeignKey('self',null=True, blank=True, on_delete=models.deletion.DO_NOTHING)
    plan = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING, related_name='plans_cases')

    def save(self, *args, **kwargs):
        self.case_id = uuid.uuid4()
        reverse_case_id=str(self.case_id)[::-1]
        self.display_id=(reverse_case_id[0:5])[::-1]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.case_id)