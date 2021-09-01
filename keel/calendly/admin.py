from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduledUrl


class CalendlyUsersAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'user_resource_url', 'event_type_resource_url')


class CalendlyCallScheduleAdmin(CustomBaseModelAdmin):
    list_display = ('call_schedule', 'invitee_url', 'cancel_url', 'reschedule_url')


class CalendlyInviteeScheduledUrlAdmin(CustomBaseModelAdmin):
    list_display = ('invitee_user', 'host_user', 'schedule_url')


admin.site.register(CalendlyUsers)
admin.site.register(CalendlyCallSchedule)
admin.site.register(CalendlyInviteeScheduledUrl)
