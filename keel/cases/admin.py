from django.contrib import admin
# import autocomplete_all as admin
from django.contrib.auth import get_user_model
from .models import Case

User = get_user_model()

class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'user', 'agent', 'is_active')
    ordering = ('case_id',)
    search_fields = ['case_id']
    autocomplete_fields = ['user', 'agent']
    readonly_fields=('deleted_at', 'case_id', 'display_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(user_type=User.CUSTOMER)
        if db_field.name == "agent":
            kwargs["queryset"] = User.objects.filter(user_type=User.RCIC)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Case, CaseAdmin)