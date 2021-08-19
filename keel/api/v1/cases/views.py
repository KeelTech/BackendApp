import logging

from keel.api.permissions import IsRCICUser
from keel.api.v1.auth.serializers import (BaseProfileSerializer,
                                          CustomerQualificationsSerializer)
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case
from keel.tasks.models import Task
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import CasesSerializer

logger = logging.getLogger('app-logger')


class CaseView(generics.CreateAPIView):
    serializer_class = CasesSerializer
    authentication_classes = (JWTAuthentication,) 
    permission_classes = (permissions.IsAuthenticated,) 
    queryset = Case.objects.all()


class FilterUserCases(generics.ListAPIView):
    serializer_class = CasesSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)

    def get(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        user = request.user
        req_data = request.GET.dict()
        queryset = Case.objects.get_agent_cases(user, req_data)
        serializer = self.serializer_class(queryset, many=True)
        response["message"] = serializer.data
        return Response(response)

  
class FilterUserCasesDetails(GenericViewSet):

    serializer_class = CasesSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_case(self, request, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        pk = kwargs.get('case_id')
        try:
            queryset = Case.objects.get(case_id=pk)
            serializer_cases = self.serializer_class(queryset)
            
            # get all user qualifications
            qualifications = queryset.user.user_qualification.all()
            serializer_qua = CustomerQualificationsSerializer(qualifications, many=True)
            
            # get user profile
            serializer_profile = BaseProfileSerializer(queryset.user.user_profile)
            
            # get number of tasks related to cases from Task Model
            tasks = Task.objects.filter(case=queryset).count()
            
            data = {
                "case_details" : serializer_cases.data,
                "user_qualifications" : serializer_qua.data,
                "user_details" : serializer_profile.data,
                "task_count" : tasks
            }
        except Exception as e:
            logger.error('ERROR: CASE:FilterUserCasesDetails ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        response["message"] = data
        return Response(response)
