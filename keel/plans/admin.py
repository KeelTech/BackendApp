from django.contrib import admin
from .models import Plan, Vendor, Service
# Register your models here.

admin.site.register(Plan)
admin.site.register(Vendor)
admin.site.register(Service)