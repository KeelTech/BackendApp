from django.contrib import admin
from .models import (User, CustomToken, PasswordResetToken, UserService, 
                    CustomerProfile, CustomerQualifications, QualificationLabel, WorkExperienceLabel,
                    CustomerWorkExperience, CustomerProfileLabel, RelativeInCanada, RelativeInCanadaLabel,
                    EducationalCreationalAssessment, EducationalCreationalAssessmentLabel)


class UserAdmin(admin.ModelAdmin):
    search_fields = ['email']

admin.site.register(User, UserAdmin)
admin.site.register(UserService)
admin.site.register(PasswordResetToken)
admin.site.register(CustomToken)
admin.site.register(CustomerProfile)
admin.site.register(CustomerProfileLabel)
admin.site.register(CustomerQualifications)
admin.site.register(QualificationLabel)
admin.site.register(CustomerWorkExperience)
admin.site.register(WorkExperienceLabel)
admin.site.register(RelativeInCanada)
admin.site.register(RelativeInCanadaLabel)
admin.site.register(EducationalCreationalAssessment)
admin.site.register(EducationalCreationalAssessmentLabel)