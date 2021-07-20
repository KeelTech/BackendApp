from django.contrib import admin
from .models import User, CustomToken, PasswordResetToken, UserService, CustomerProfile, CustomerQualifications

admin.site.register(User)
admin.site.register(CustomToken)
admin.site.register(PasswordResetToken)
admin.site.register(UserService)
admin.site.register(CustomerProfile)
admin.site.register(CustomerQualifications)