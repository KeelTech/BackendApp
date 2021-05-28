from rest_framework import permissions
from django.conf import settings


class CustomLeadPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        header = request.headers['X-CLIENT_ID']

        if header == settings.LEADAPITOKEN:
            return True

        return False