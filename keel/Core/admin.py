from django.contrib import admin
from .models import Country, City, State
# Register your models here.

class CountryAdmin(admin.ModelAdmin):
    readonly_fields = ('deleted_at', )

class StateAdmin(admin.ModelAdmin):
    readonly_fields = ('deleted_at', )

class CityAdmin(admin.ModelAdmin):
    readonly_fields = ('deleted_at', )


admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)