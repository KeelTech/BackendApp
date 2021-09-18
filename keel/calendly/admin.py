from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduledUrl


class CalendlyUsersAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'user_url', 'event_type_url')


class CalendlyCallScheduleAdmin(CustomBaseModelAdmin):
    list_display = ('call_schedule', 'invitee_url', 'cancel_url', 'reschedule_url')


class CalendlyInviteeScheduledUrlAdmin(CustomBaseModelAdmin):
    list_display = ('invitee_user', 'host_user', 'scheduled_call_url')


admin.site.register(CalendlyUsers, CalendlyUsersAdmin)
admin.site.register(CalendlyCallSchedule, CalendlyCallScheduleAdmin)
admin.site.register(CalendlyInviteeScheduledUrl, CalendlyInviteeScheduledUrlAdmin)
