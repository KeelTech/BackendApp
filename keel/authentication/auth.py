from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.GET.get("username")

        if not username:  # no username passed in request headers
            return None  # authentication did not succeed

        try:
            user = User.objects.get(username=username)  # get the user
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)  # authentication successful
