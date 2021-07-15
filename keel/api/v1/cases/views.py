from django.db.models import query
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, generics
from rest_framework.response import Response

from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case
from keel.api.permissions import IsRCICUser

from .serializers import ListCasesSerializer


class FilterUserCases(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)

    def list(self, request):
        user = request.user
        queryset = Case.objects.filter(agent=user)
        serializer = ListCasesSerializer(queryset, many=True)
        return Response(serializer.data)


class FilterUserCasesDetails(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Case.objects.all()
    serializer_class = ListCasesSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )