from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from keel.authentication.backends import JWTAuthentication
from keel.tasks.models import Task
from keel.cases.models import Case
from keel.api.permissions import IsRCICUser

from .serializers import CasesSerializer

import logging
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
        response["message"] = data
        return Response(response)


class FilterUserCasesDetails(GenericViewSet):

    serializer_class = CasesSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_case(self,request, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        pk = kwargs.get('pk')
        try:
            queryset = Case.objects.get(case_id=pk)
            tasks = Task.objects.filter(case=queryset).count()
            data = []
            data.append({
                "case_details" : {
                    "case_id" : queryset.case_id,
                    "account_manager_id" : queryset.account_manager_id,
                    "status" : queryset.status,
                    "is_active" : queryset.is_active
                },
                "user_details" : {
                    "fullname" : "{} {}".format(queryset.user.user_profile.first_name, queryset.user.user_profile.last_name),
                    "mother_fullname" : queryset.user.user_profile.mother_fullname,
                    "father_fullname" : queryset.user.user_profile.father_fullname,
                    "age" : queryset.user.user_profile.age,
                    "address" : queryset.user.user_profile.address,
                    "date_of_birth" : queryset.user.user_profile.date_of_birth,
                },
                "user_qualifications" : {
                    "institute_name" : queryset.user.user_qualification.institute_name,
                    "grade" : queryset.user.user_qualification.grade,
                    "year_of_passing" : queryset.user.user_qualification.year_of_passing,
                    "start_date" : queryset.user.user_qualification.start_date,
                    "city" : queryset.user.user_qualification.city,
                    "country" : queryset.user.user_qualification.country,
                },
                "task_count" : tasks
            })
        except Exception as e:
            logger.error('ERROR: CASE:FilterUserCasesDetails ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        response["message"] = data
        return Response(response)