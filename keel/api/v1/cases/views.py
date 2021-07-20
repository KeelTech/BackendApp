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
                "status": cases.status,
                "is_active": cases.is_active,
                "start_date": cases.created_at,
                "updated_at": cases.updated_at,
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
        pk = kwargs.get('case_id')
        try:
            queryset = Case.objects.get(case_id=pk)
            # get all user qualifications
            qualifications = queryset.user.user_qualification.all()
            user_qua = []
            for qualification in qualifications:
                user_qua.append({
                     "institute_name" : qualification.institute_name,
                    "grade" : qualification.grade,
                    "year_of_passing" : qualification.year_of_passing,
                    "start_date" : qualification.start_date,
                    "city" : qualification.city,
                    "country" : qualification.country,
                })
            
            # get number of tasks related to cases from Task Model
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
                "user_qualifications" : user_qua,
                "task_count" : tasks
            })
        except Exception as e:
            logger.error('ERROR: CASE:FilterUserCasesDetails ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        response["message"] = data
        return Response(response)