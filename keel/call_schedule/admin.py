from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import CallSchedule


class CallScheduleAdmin(CustomBaseModelAdmin):
    autocomplete_fields = ('visitor_user', 'host_user', )
    list_display = ('visitor_user', 'host_user', 'call_schedule_client_type', 'status', 'is_active')


admin.site.register(CallSchedule, CallScheduleAdmin)
