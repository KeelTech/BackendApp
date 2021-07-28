from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Case

User = get_user_model()


class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'user', 'agent', 'is_active')
    ordering = ('case_id',)
    search_fields = ['user', 'agent']
    autocomplete_fields = ['user', 'agent']
    readonly_fields=('deleted_at',)

    # def get_queryset(self, request):
    #     qs = super(CaseAdmin, self).get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CaseAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['user'].queryset = User.objects.filter(user_type="1")
        form.base_fields['agent'].queryset = User.objects.filter(user_type="2")
        return form

admin.site.register(Case, CaseAdmin)