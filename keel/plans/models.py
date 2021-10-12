from django.db import models
import uuid
from django.db.models.deletion import DO_NOTHING
from django.contrib.postgres.fields import ArrayField
from keel.Core.models import TimeStampedModel, SoftDeleteModel


class PlatformComponents(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=512, default=None, null=True, blank=True)
    description = models.CharField(max_length=512, default=None, null=True, blank=True)

    def __str__(self):
        return self.name


class Plan(TimeStampedModel, SoftDeleteModel):
    FREE_PLAN_TYPE = 1
    CALLING_PLAN_TYPE = 2
    PREMIUM_PLAN_TYPE = 3

    PLAN_TYPE_CHOICES = (
        (FREE_PLAN_TYPE, "Free Plan"),
        (CALLING_PLAN_TYPE, "Calling Plan"),
        (PREMIUM_PLAN_TYPE, "Premium Plan")
    )
    title = models.CharField(max_length=512, null=True, default=None, blank=True)
    type = models.PositiveSmallIntegerField(choices=PLAN_TYPE_CHOICES, default=FREE_PLAN_TYPE)
    description = models.TextField(null=True, blank=True, default=None)
    discount = models.PositiveSmallIntegerField(default=0, blank=True, null=True) # in percentage
    price = models.FloatField(null=True, blank=True, default=True)
    currency = models.CharField(max_length=10, null=True, blank=True, default=None)
    country_iso = models.CharField(max_length=512, null=True, blank=True, default=None)
    check_list = ArrayField(models.TextField(), blank=True, default=list)
    sgst = models.PositiveSmallIntegerField(default=0, null=True, blank=True) # in percentage
    cgst = models.PositiveSmallIntegerField(default=0, null=True, blank=True) # in percentage
    platform_components = models.ManyToManyField(PlatformComponents, through='PlanPlatformComponents')
    is_active = models.BooleanField(default=True)

    def get_plan(self):
        return self
    
    def get_discount_price(self):
        discount = self.discount/100
        discount_price = self.price - (self.price*discount)
        return discount_price

    def get_total_amount(self):
        return self.price

    def get_payment_amount(self):
        return self.price

    def get_currency(self):
        return self.currency

    def get_case(self):
        return None

    def update_case(self, case_model_obj):
        return None

    def complete_payment(self):
        pass

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.title)


class PlanPlatformComponents(TimeStampedModel):
    plan = models.ForeignKey(Plan, models.DO_NOTHING)
    platform_components = models.ForeignKey(PlatformComponents, models.DO_NOTHING)

    class Meta:
        unique_together = [
            ('plan', 'platform_components'),
        ]


class Vendor(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=512, null=True, blank=True, default=None)

    def __str__(self):
        return self.name

class Service(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=512, null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=False)
    fulfillment = models.ForeignKey(Vendor,verbose_name="Vendor", related_name="Vendors", null=True, blank=True, default=None, on_delete=DO_NOTHING)
    price = models.FloatField(null=True, blank=True, default=None)
    currency = models.CharField(max_length=512, null=True, blank=True, default=None) 
    country_iso = models.CharField(max_length=512, null=True, blank=True, default=None)
    plans = models.ManyToManyField(Plan, through = "ServicesPlans", blank = True)

    def get_plan(self):
        return None

    def get_total_amount(self):
        return self.price

    def get_payment_amount(self):
        return self.price

    def get_currency(self):
        return self.currency
    
    def __str__(self):
        return self.title

    def get_case(self):
        return None

    def update_case(self, case_model_obj):
        return None

    def complete_payment(self):
        pass


class ServicesPlans(TimeStampedModel, SoftDeleteModel):

    plan = models.ForeignKey(Plan, on_delete=models.deletion.DO_NOTHING, related_name='plans_services')
    service = models.ForeignKey(Service, on_delete=models.deletion.DO_NOTHING, related_name='services_plans')

    def __str__(self):
        return self.plan

