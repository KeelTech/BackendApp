from django.db.models import query
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, generics
from rest_framework.response import Response

from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import CustomerProfile
from keel.cases.models import Case
from keel.api.permissions import IsRCICUser

from keel.api.v1.auth.serializers import CustomerProfileSerializer, CustomerQualificationsSerializer
from .serializers import ListCasesSerializer


class FilterUserCases(APIView):
    serializer_class = ListCasesSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)

    def get(self, request):
        user = request.user
        queryset = Case.objects.filter(agent=user)
        data = []
        for cases in queryset:
            data.append({
                "case_id": cases.case_id,
                "user": cases.user.email,
                "account_manager_id": cases.account_manager_id,
                "agent": cases.agent.email,
                "plan": cases.plan.title,
                "is_active": cases.is_active,
            })
        return Response(data)


class FilterUserCasesDetails(generics.ListAPIView):

    serializer_class = ListCasesSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_queryset(self):
        queryset = Case.objects.filter(pk=self.kwargs['pk'])
        return queryset