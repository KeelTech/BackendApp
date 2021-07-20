from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions, generics, status
from rest_framework.response import Response

from keel.authentication.backends import JWTAuthentication
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
        queryset = Case.objects.filter(pk=self.kwargs['pk'])
        data = []
        try:
            for case in queryset:
                data.append({
                    "case_details" : {
                        "case_id" : case.case_id,
                        "account_manager_id" : case.account_manager_id,
                        "status" : case.status,
                        "is_active" : case.is_active
                    },
                    "user_details" : {
                        "fullname" : "{} {}".format(case.user.user_profile.first_name, case.user.user_profile.last_name),
                        "mother_fullname" : case.user.user_profile.mother_fullname,
                        "father_fullname" : case.user.user_profile.father_fullname,
                        "age" : case.user.user_profile.age,
                        "address" : case.user.user_profile.address,
                        "date_of_birth" : case.user.user_profile.date_of_birth,
                    },
                    "user_qualifications" : {
                        "institute_name" : case.user.user_qualification.institute_name,
                        "grade" : case.user.user_qualification.grade,
                        "year_of_passing" : case.user.user_qualification.year_of_passing,
                        "start_date" : case.user.user_qualification.start_date,
                        "city" : case.user.user_qualification.city,
                        "country" : case.user.user_qualification.country,
                    }
                })
        except Exception as e:
            logger.error('ERROR: CASE:FilterUserCasesDetails ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        response["message"] = data
        return Response(response)