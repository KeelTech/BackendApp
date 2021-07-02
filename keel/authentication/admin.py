from django.contrib import admin
from .models import User, CustomToken, PasswordResetToken

admin.site.register(User)
admin.site.register(CustomToken)
admin.site.register(PasswordResetToken)