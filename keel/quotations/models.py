from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User
from keel.plans.models import Plan

# Create your models here.

class Quotation(TimeStampedModel, SoftDeleteModel):
    
    ACCEPTED = 1
    REJECTED = 2

    QUO_STATUS_TYPE_CHOICES = (
        (ACCEPTED, 'Accpeted'),
        (REJECTED, 'Rejected'),
    )

    q_id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, 
                                    related_name = "user_quotaions", blank = True, null = True ) 
    account_manager_id = models.IntegerField(null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete = models.deletion.DO_NOTHING,
                                    related_name = "plan_quotations")
    total_amount = models.DecimalField(max_digits = 12, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=QUO_STATUS_TYPE_CHOICES, 
                                        verbose_name="quo_status", default=ACCEPTED)

class QuotationMilestone(TimeStampedModel, SoftDeleteModel):

    PAID = 1
    UNPAID = 2

    QUO_MILESTONES_STATUS_TYPE_CHOICES = (
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    )
    qm_id = models.CharField(max_length=255, primary_key=True)
    due_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits = 12, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=QUO_MILESTONES_STATUS_TYPE_CHOICES, 
                                                verbose_name="quo_milestone_status", default=UNPAID)
    description = models.TextField(null=True,blank=True)
    quotation = models.ForeignKey(Quotation, on_delete = models.deletion.DO_NOTHING, 
                                    related_name = "milestones_quote")

