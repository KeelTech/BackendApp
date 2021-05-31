from django.db import models
from keel.leads.models import CustomerLead

# Create your models here.


class EligibilityResults(models.Model):

    lead_id = models.ForeignKey(CustomerLead, on_delete=models.DO_NOTHING, related_name="lead_id", null=True)
    data = models.JSONField(verbose_name="Data", null=True)

    def __str__(self):
        return self.data['name']

    class Meta:
        db_table = "eligibility_results"

