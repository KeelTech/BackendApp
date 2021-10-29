from django.contrib import admin
from .models import InAppNotification

class InAppNotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(InAppNotification, InAppNotificationAdmin)