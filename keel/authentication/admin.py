from django.contrib import admin
from .models import (User, CustomToken, PasswordResetToken, UserService, 
                    CustomerProfile, CustomerQualifications, QualificationLabel, WorkExperienceLabel,
                    CustomerWorkExperience, CustomerProfileLabel)


class UserAdmin(admin.ModelAdmin):
    search_fields = ['user_type']

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