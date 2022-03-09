from django.contrib import admin
from .models import InAppNotification

class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'case_id', 'user_id', 'seen')

admin.site.register(InAppNotification, InAppNotificationAdmin)