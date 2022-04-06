from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Web, HomeLeads, WebsiteContactData, WebsiteComponents

class WebsiteComponenetsAdmin(CustomBaseModelAdmin):
    list_display = ('title', 'component_name', )


admin.site.register(Web)
admin.site.register(HomeLeads)
admin.site.register(WebsiteContactData)
admin.site.register(WebsiteComponents, WebsiteComponenetsAdmin)