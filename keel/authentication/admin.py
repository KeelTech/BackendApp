from django.contrib import admin
from .models import User, CustomToken, PasswordResetToken, UserService, CustomerProfile, CustomerQualifications


class UserAdmin(admin.ModelAdmin):
    search_fields = ['user_type']

admin.site.register(User, UserAdmin)
admin.site.register(CustomToken)
admin.site.register(PasswordResetToken)
admin.site.register(UserService)
admin.site.register(CustomerProfile)
admin.site.register(CustomerQualifications)