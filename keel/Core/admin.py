from django.contrib import admin
from .models import Country, City, State, TriggeredEmails
# Register your models here.

class CustomBaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('deleted_at', )

class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    readonly_fields = ('deleted_at', )

class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'state')
    readonly_fields = ('deleted_at', )

class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'state', 'city_name')
    readonly_fields = ('deleted_at', )

class TriggerEmailAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'email', 'subject')


admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(TriggeredEmails, TriggerEmailAdmin)