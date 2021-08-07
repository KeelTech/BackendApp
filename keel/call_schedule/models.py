import uuid
from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User


class CallSchedule(TimeStampedModel, SoftDeleteModel):
    ACTIVE = 1
    RESCHEDULED = 2
    CANCELED = 3
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (RESCHEDULED, 'Rescheduled'),
        (CANCELED, 'Canceled')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor_user = models.ForeignKey(User, verbose_name="Customer",
                                     on_delete=models.DO_NOTHING, related_name="customer_call_schedules")
    host_user = models.ForeignKey(User, verbose_name="RCIC or Account Manager",
                                  on_delete=models.DO_NOTHING, related_name="call_schedules")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE)
    start_time = models.DateTimeField(verbose_name="Starting time of call schedule in UTC from calendly")
    end_time = models.DateTimeField(verbose_name="Ending time of call schedule in UTC from calendly")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "call_schedule"
