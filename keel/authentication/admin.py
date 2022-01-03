from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from django.db.models import query, Q
from .models import (User, CustomToken, PasswordResetToken, UserService, 
                    CustomerProfile, CustomerQualifications, QualificationLabel, WorkExperienceLabel,
                    CustomerWorkExperience, CustomerProfileLabel, RelativeInCanada, RelativeInCanadaLabel,
                    EducationalCreationalAssessment, EducationalCreationalAssessmentLabel, AgentProfile, 
                    AccountManagerProfile, UserDocument, SMSOtpModel)
from keel.Core.models import Country, State, City

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'user_type', 'is_active', 'is_verified', 'is_staff']
    search_fields = ['email']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if 'autocomplete' in request.path:
            field_name = request.GET.get('field_name')
            user = ['user', 'customer']
            agent = ['agent', 'rcic', 'account manager']
            if field_name.lower() in user:
                queryset = queryset.filter(user_type=User.CUSTOMER)
            if field_name.lower() in agent:
                queryset = queryset.filter(Q(user_type=User.RCIC) | Q(user_type=User.ACCOUNT_MANAGER))
        return queryset, use_distinct

class UserServiceAdmin(CustomBaseModelAdmin):
    pass

class CustomerProfileAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'age',)
    autocomplete_fields = ('user', )

class AgentProfileAdmin(CustomBaseModelAdmin):
    list_display = ('agent', 'full_name', 'license', 'country')
    autocomplete_fields = ('agent', )
    readonly_fields = ('deleted_at', )

class AccountManagerProfileAdmin(AgentProfileAdmin):
    pass

class CustomerProfileLabelAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at', )

class CustomerQualificationsAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'institute', 'country', 'start_date', 'end_date')
    readonly_fields = ('deleted_at', )

    class Media:
        js = ("selectajax.js", )

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            form = super(CustomerQualificationsAdmin, self).get_form(request, obj, **kwargs)
            form.base_fields['state'].queryset = State.objects.filter(country=obj.country)
            form.base_fields['city'].queryset = City.objects.filter(state=obj.state)
            return form
        return super().get_form(request, obj=obj, **kwargs)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     print(kwargs)
    #     if db_field.name == "state":
    #         kwargs['queryset'] = State.objects.filter()
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
class QualificationLabelAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at', )

class CustomerWorkExperienceAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'company_name', 'designation', 'start_date', 'end_date')
    readonly_fields = ('deleted_at', )

    class Media:
        js = ("selectajax.js", )

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            form = super(CustomerWorkExperienceAdmin, self).get_form(request, obj, **kwargs)
            form.base_fields['state'].queryset = State.objects.filter(country=obj.country)
            form.base_fields['city'].queryset = City.objects.filter(state=obj.state)
            return form
        return super().get_form(request, obj=obj, **kwargs)

class WorkExperienceLabelAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at', )

class RelativeInCanadaAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'full_name', 'email_address', 'relationship', 'immigration_status')
    readonly_fields = ('deleted_at', )

class RelativeInCanadaLabelAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at', )

class EducationalCreationalAssessmentAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'eca_authority_name', 'eca_authority_number', 'canadian_equivalency_summary')
    readonly_fields = ('deleted_at', )

class EducationalCreationalAssessmentLabelAdmin(CustomBaseModelAdmin):
    readonly_fields = ('deleted_at', )


class UserDocumentAdmin(CustomBaseModelAdmin):
    list_display = ('user', 'doc', 'task')

admin.site.register(User, UserAdmin)
admin.site.register(SMSOtpModel)
admin.site.register(UserService, UserServiceAdmin)
admin.site.register(PasswordResetToken)
admin.site.register(CustomToken)
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(AgentProfile, AgentProfileAdmin)
admin.site.register(AccountManagerProfile, AccountManagerProfileAdmin)
admin.site.register(CustomerProfileLabel, CustomerProfileLabelAdmin)
admin.site.register(CustomerQualifications, CustomerQualificationsAdmin)
admin.site.register(QualificationLabel, QualificationLabelAdmin)
admin.site.register(CustomerWorkExperience, CustomerWorkExperienceAdmin)
admin.site.register(WorkExperienceLabel, WorkExperienceLabelAdmin)
admin.site.register(RelativeInCanada, RelativeInCanadaAdmin)
admin.site.register(RelativeInCanadaLabel, RelativeInCanadaLabelAdmin)
admin.site.register(EducationalCreationalAssessment, EducationalCreationalAssessmentAdmin)
admin.site.register(EducationalCreationalAssessmentLabel, EducationalCreationalAssessmentLabelAdmin)
admin.site.register(UserDocument, UserDocumentAdmin)
