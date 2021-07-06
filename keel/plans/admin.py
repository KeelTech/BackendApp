from django.contrib import admin
from .models import Plans, Vendors, Services
# Register your models here.

admin.site.register(Plans)
admin.site.register(Vendors)
admin.site.register(Services)