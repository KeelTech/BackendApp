from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import datetime, calendar
from django.conf import settings
from rest_framework import authentication, exceptions
import base64


User = get_user_model()


class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username, 'user_type': 1}
        else:
            kwargs = {'phone_number': username, 'user_type': 1}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
