from django.db import models
from django.conf import settings
from datetime import datetime


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