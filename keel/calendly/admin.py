from django.contrib import admin
from .models import CalendlyUsers


class CalendlyUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_resource_url', 'event_type_resource_url')


admin.site.register(CalendlyUsers)
