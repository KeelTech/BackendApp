from rest_framework import permissions
from django.conf import settings


class CustomLeadPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        header = request.headers.get('X-CLIENT_ID')

        if header == settings.LEADAPITOKEN:
            return True

        return False


class IsRCICUser(permissions.BasePermission):

    def has_permission(self, request, view):
        
        user = request.user

        """
        user type 2 == RCIC, 1 = CUSTOMER, since we're checking is user is RCIC, 
        then we check if user.user_type = 2
        """
        
        if user.user_type == user.RCIC: 
            return True
        
        return False