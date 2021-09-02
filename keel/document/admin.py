from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import DocumentType, Documents, PublicDocuments

# Register your models here.
admin.site.register(Documents, CustomBaseModelAdmin)
admin.site.register(DocumentType, CustomBaseModelAdmin)
admin.site.register(PublicDocuments, CustomBaseModelAdmin)
