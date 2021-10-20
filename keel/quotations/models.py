import uuid

from django.db import models
from keel.authentication.models import User
from keel.cases.models import Case
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.plans.models import Plan

# Create your models here.


class Quotation(TimeStampedModel, SoftDeleteModel):
    
    CREATED = 1
    ACCEPTED = 2
    REJECTED = 3

    QUO_STATUS_TYPE_CHOICES = (
        (CREATED, 'CREATED'),
        (ACCEPTED, 'ACCEPTED'),
        (REJECTED, 'REJECTED'),
    )

    q_id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING,
                             related_name="user_quotations", blank=True, null=True)
    case = models.ForeignKey(Case, on_delete=models.deletion.DO_NOTHING,
                             related_name="case_quotations", blank=True, null=True)
    account_manager_id = models.IntegerField(null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING,
                             related_name="plan_quotations")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=QUO_STATUS_TYPE_CHOICES,
                                              verbose_name="quo_status", default=CREATED)

    def save(self, *args, **kwargs):
        if not self.q_id:
            self.q_id = uuid.uuid4()
        super().save(*args, **kwargs)

    def get_currency(self):
        return self.plan.get_currency()

    def get_case(self):
        return self.case


class QuotationMilestone(TimeStampedModel, SoftDeleteModel):

    PAID = 1
    UNPAID = 2

    QUO_MILESTONES_STATUS_TYPE_CHOICES = (
        (PAID, 'Paid'),
        (UNPAID, 'Unpaid'),
    )
    qm_id = models.CharField(max_length=255, primary_key=True)
    due_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=QUO_MILESTONES_STATUS_TYPE_CHOICES,
                                              verbose_name="quo_milestone_status", default=UNPAID)
    description = models.TextField(null=True, blank=True)
    quotation = models.ForeignKey(Quotation, on_delete=models.deletion.DO_NOTHING,
                                  related_name="milestones_quote")

    def get_plan(self):
        return self.quotation.plan

    def get_total_amount(self):
        return self.quotation.total_amount

    def get_payment_amount(self):
        return self.amount

    def get_currency(self):
        return self.quotation.get_currency()

    def get_case(self):
        return self.quotation.get_case()

    def update_case(self, case_model_obj):
        quotation = Quotation.objects.select_for_update().get(pk=self.quotation.pk)
        if not quotation.case:
            quotation.case = case_model_obj
            quotation.save()

    def complete_payment(self):
        self.status = self.PAID
        self.save()
