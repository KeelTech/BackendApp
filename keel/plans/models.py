from django.db import models
import uuid
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields import PositiveIntegerRelDbTypeMixin
from keel.Core.models import TimeStampedModel, SoftDeleteModel

class Plan(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=512, null=True, default=None, blank=True)
    description = models.TextField(null=True, blank=True, default=None)
    price = models.FloatField(null=True, blank=True, default=True)
    currency = models.CharField(max_length=10, null=True, blank=True, default=None)
    country_iso = models.CharField(max_length=512, null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.title)


class Vendor(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=512, null=True, blank=True, default=None)


class Service(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=512, null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=False)
    fulfillment = models.ForeignKey(Vendor,verbose_name="Vendor", related_name="Vendors", null=True, blank=True, default=None, on_delete=DO_NOTHING)
    price = models.FloatField(null=True, blank=True, default=None)
    currency = models.CharField(max_length=512, null=True, blank=True, default=None) 
    country_iso = models.CharField(max_length=512, null=True, blank=True, default=None)