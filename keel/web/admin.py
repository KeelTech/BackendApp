from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin

from .models import (
    EmailTemplateModel,
    HomeLeads,
    Web,
    WebsiteComponents,
    WebsiteContactData,
)


class WebsiteComponenetsAdmin(CustomBaseModelAdmin):
    list_display = (
        "title",
        "component_name",
    )

class EmailTemplateModelAdmin(CustomBaseModelAdmin):
    pass


admin.site.register(Web)
admin.site.register(HomeLeads)
admin.site.register(WebsiteContactData)
admin.site.register(WebsiteComponents, WebsiteComponenetsAdmin)
admin.site.register(EmailTemplateModel, EmailTemplateModelAdmin)
