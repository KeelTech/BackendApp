from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers, status, generics
from rest_framework import permissions

from keel.authentication.backends import JWTAuthentication
from keel.plans.models import Plan
from .serializers import PlanSerializers


class PlanListView(generics.ListAPIView):
    serializer_class = PlanSerializers
    permission_classes = (permissions.AllowAny, )
    
    def get_queryset(self):
        queryset = Plan.objects.filter(is_active=True)
        return queryset