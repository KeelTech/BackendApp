from django.db import models
from django.utils import timezone
from keel.leads.models import CustomerLead
from keel.Core.models import TimeStampedModel
# Create your models here.


class EligibilityResults(TimeStampedModel):

    lead_id = models.ForeignKey(CustomerLead, on_delete=models.DO_NOTHING, related_name="lead_id", null=True)
    data = models.JSONField(verbose_name="Data", null=True)

    def __str__(self):
        return self.data['name']

    class Meta:
        db_table = "eligibility_results"

