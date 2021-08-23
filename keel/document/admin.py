from django.contrib import admin
from .models import DocumentType, Documents, PublicDocuments

# Register your models here.
admin.site.register(Documents)
admin.site.register(DocumentType)
admin.site.register(PublicDocuments)
