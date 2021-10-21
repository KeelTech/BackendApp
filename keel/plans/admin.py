from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Plan, PlatformComponents, Vendor, Service, ServicesPlans, PlanPlatformComponents
# Register your models here.

class PlanPlatformInline(admin.TabularInline):
    model = PlanPlatformComponents    
    extra = 0

class PlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'currency')
    search_fields = ('title', )
    readonly_fields=('deleted_at',)
    inlines = [PlanPlatformInline]


class PlatformComponentsAdmin(admin.ModelAdmin):
    readonly_fields = ('deleted_at', )

class VendorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields=('deleted_at',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'fulfillment', 'price', 'currency')
    autocomplete_fields = ['fulfillment']
    readonly_fields=('deleted_at',)

admin.site.register(Plan, PlanAdmin)
admin.site.register(PlatformComponents,PlatformComponentsAdmin)
admin.site.register(PlanPlatformComponents)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServicesPlans, CustomBaseModelAdmin)

