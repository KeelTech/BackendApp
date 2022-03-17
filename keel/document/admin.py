from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import DocumentType, Documents, PublicDocuments

# Register your models here.
admin.site.register(Documents, CustomBaseModelAdmin)
admin.site.register(DocumentType, CustomBaseModelAdmin)



class PublicDocumentAdmin(CustomBaseModelAdmin):
	list_display = ('original_name', 'file_link')
	
	def file_link(self, obj):
		if obj and obj.avatar and obj.avatar.url:
			return obj.avatar.url
		return ""

	# file_link.allow_tags = True

admin.site.register(PublicDocuments, PublicDocumentAdmin)