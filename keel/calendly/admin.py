from django.contrib import admin
from .models import CalendlyUsers, CalendlyCallSchedule


class CalendlyUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_resource_url', 'event_type_resource_url')


class CalendlyCallScheduleAdmin(admin.ModelAdmin):
    list_display = ('call_schedule', 'scheduled_event_invitee_url', 'cancel_call_url', 'reschedule_call_url')


admin.site.register(CalendlyUsers)
admin.site.register(CalendlyCallSchedule)
