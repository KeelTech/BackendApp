from django.contrib import admin
# import autocomplete_all as admin
from django.contrib.auth import get_user_model
from .models import Case, Program, AgentNotes

User = get_user_model()

class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'user', 'agent', 'program', 'is_active')
    ordering = ('case_id',)
    search_fields = ['case_id']
    autocomplete_fields = ['user', 'agent', 'account_manager']
    readonly_fields=('deleted_at', 'case_id', 'display_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(user_type=User.CUSTOMER)
        if db_field.name == "agent":
            kwargs["queryset"] = User.objects.filter(user_type=User.RCIC)
        if db_field.name == "account_manager":
            kwargs["queryset"] = User.objects.filter(user_type=User.ACCOUNT_MANAGER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('choice', 'category')
    readonly_fields = ['deleted_at']

admin.site.register(Case, CaseAdmin)
admin.site.register(AgentNotes)
admin.site.register(Program, ProgramAdmin)