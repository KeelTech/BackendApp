from django.contrib import admin
from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduledUrl


class CalendlyUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_resource_url', 'event_type_resource_url')


class CalendlyCallScheduleAdmin(admin.ModelAdmin):
    list_display = ('call_schedule', 'invitee_url', 'cancel_url', 'reschedule_url')


class CalendlyInviteeScheduledUrlAdmin(admin.ModelAdmin):
    list_display = ('invitee_user', 'host_user', 'schedule_url')


admin.site.register(CalendlyUsers)
admin.site.register(CalendlyCallSchedule)
admin.site.register(CalendlyInviteeScheduledUrl)
