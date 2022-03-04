from django.db import models
from django.conf import settings
from datetime import datetime
from django.db.models.fields import BooleanField


import pytz

# Create your models here.
class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, db_index = True)

    def mark_delete(self):
        self.deleted_at = datetime.now(pytz.timezone(settings.TIME_ZONE))
        self.save()

    class Meta:
        abstract = True


class Country(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255, default=None, blank=True, null=True)
    numeric_code = models.CharField(max_length=255, default=None, blank=True, null=True)
    phone_code = models.CharField(max_length=255, default=None, blank=True, null=True)
    capital = models.CharField(max_length=255, default=None, blank=True, null=True)
    currency = models.CharField(max_length=255, default=None, blank=True, null=True)
    currency_symbol = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-id']


class State(TimeStampedModel, SoftDeleteModel):
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="country",
                                    default=None, blank=True, null=True)
    state = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.state)


class City(TimeStampedModel, SoftDeleteModel):
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name="city_state",
                                    default=None, null=True, blank=True)
    city_name = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.city_name)


class TriggeredEmails(TimeStampedModel, SoftDeleteModel):
    # user = models.Cha(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    email = models.CharField(max_length=255, default=None, blank=True, null=True)
    subject = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.email)
    