from rest_framework import permissions
from django.conf import settings


class CustomLeadPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        header = request.headers.get('X-CLIENT_ID')

        if header == settings.LEADAPITOKEN:
            return True

        return False


# class IsAgentOrAccountManager(permissions.BasePermission):

#     def has_permission(self, request, view):
        
#         user = request.user
        
#         if user.user_type == user.RCIC or user.user_type == user.ACCOUNT_MANAGER: 
#             return True
        
#         return False

class IsRCICUser(permissions.BasePermission):

    def has_permission(self, request, view):
        
        user = request.user
        
        if user.user_type == user.RCIC or user.user_type == user.ACCOUNT_MANAGER:
            return True
        
        return False

# class IsAccountManager(permissions.BasePermission):

#     def has_permission(self, request, view):
        
#         user = request.user
        
#         if user.user_type == user.ACCOUNT_MANAGER: 
#             return True
        
#         return False