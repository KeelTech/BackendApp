import uuid
from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User


class CallSchedule(TimeStampedModel, SoftDeleteModel):
    ACTIVE = 1
    RESCHEDULED = 2
    CANCELED = 3
    COMPLETED = 4
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (RESCHEDULED, 'Rescheduled'),
        (CANCELED, 'Canceled'),
        (COMPLETED, 'Completed'),
    )
    STATUS_MAP = {
        ACTIVE: "active",
        RESCHEDULED: "rescheduled",
        CANCELED: "canceled",
        COMPLETED: "completed"
    }
    CALENDLY_CALL_SCHEDULE_CLIENT = 1
    CALL_SCHEDULE_CLIENT_CHOICES = (
        (CALENDLY_CALL_SCHEDULE_CLIENT, "Calendly"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor_user = models.ForeignKey(User, verbose_name="Customer",
                                     on_delete=models.DO_NOTHING, related_name="customer_call_schedules")
    host_user = models.ForeignKey(User, verbose_name="RCIC or Account Manager",
                                  on_delete=models.DO_NOTHING, related_name="call_schedules")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=ACTIVE)
    start_time = models.DateTimeField(verbose_name="Starting time of call schedule in UTC from calendly")
    end_time = models.DateTimeField(verbose_name="Ending time of call schedule in UTC from calendly")
    call_schedule_client_type = models.PositiveSmallIntegerField(choices=CALL_SCHEDULE_CLIENT_CHOICES,
                                                                 default=CALENDLY_CALL_SCHEDULE_CLIENT)
    is_active = models.BooleanField(default=True)

    @property
    def readable_status(self):
        return self.STATUS_MAP.get(self.status)
    
    def __str__(self):
        return self.id

    class Meta:
        db_table = "call_schedule"
