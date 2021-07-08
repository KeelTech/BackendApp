from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.plans.models import Plan
from keel.authentication.models import User
# Create your models here.

class Case(TimeStampedModel, SoftDeleteModel):

    case_id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases')
    account_manager_id = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(verbose_name= 'Active', default=True)
    ref_id = models.ForeignKey('self',null=True, blank=True, on_delete=models.deletion.DO_NOTHING)
    plan_id = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING, related_name='plans_cases')



