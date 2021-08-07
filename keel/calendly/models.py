from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User
from keel.call_schedule.models import CallSchedule


class CalendlyUsers(TimeStampedModel, SoftDeleteModel):

    user = models.OneToOneField(User, verbose_name="RCIC or account manager user",
                                on_delete=models.deletion.DO_NOTHING, related_name='calendly_details')
    user_resource_url = models.CharField(max_length=1024, null=True)
    event_type_resource_url = models.CharField(max_length=1024, null=True)

    class Meta:
        db_table = "calendly_user"


class CalendlyCallSchedule(TimeStampedModel, SoftDeleteModel):
    CALL_SCHEDULE_MAP = {
        "active": CallSchedule.ACTIVE,
        "canceled": CallSchedule.CANCELED
    }
    call_schedule = models.ForeignKey(CallSchedule, on_delete=models.deletion.DO_NOTHING,
                                      related_name='calendly_schedule_details')
    scheduled_event_invitee_url = models.CharField(max_length=1024)
    cancel_call_url = models.CharField(max_length=1024, null=True)
    reschedule_call_url = models.CharField(max_length=1024, null=True)
    communication_means = models.JSONField(verbose_name="Stores communication means details from Calendly")
    status = models.PositiveSmallIntegerField(choices=CallSchedule.STATUS_CHOICES, default=CallSchedule.ACTIVE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "calendly_call_schedule"


class CalendlyInviteeScheduleUrl(TimeStampedModel, SoftDeleteModel):
    invitee_user = models.ForeignKey(User, verbose_name="Customer",
                                     on_delete=models.deletion.DO_NOTHING, related_name='calendly_schedule_url')
    host_user = models.ForeignKey(User, verbose_name="RCIC or Account Manager",
                                  on_delete=models.DO_NOTHING, related_name="calendly_invitee_sch_url")
    schedule_url = models.CharField(max_length=1024, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "calendly_invitee_schedule_url"
