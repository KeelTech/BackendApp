from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import CallSchedule

class CallScheduleAdmin(CustomBaseModelAdmin):
    autocomplete_fields = ('visitor_user', 'host_user', )

admin.site.register(CallSchedule, CallScheduleAdmin)
