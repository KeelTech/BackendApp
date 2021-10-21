import logging

from keel.api.permissions import IsRCICUser
from keel.api.v1.auth.serializers import (BaseProfileSerializer,
                                          CustomerQualificationsSerializer, CustomerWorkExperienceSerializer)
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case, Program
from keel.tasks.models import Task
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .serializers import CaseProgramSerializer, CasesSerializer, BaseCaseProgramSerializer, CaseIDSerializer

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

            # get all user work experiences
            work_experinece = queryset.user.user_workexp.all()
            serializer_work = CustomerWorkExperienceSerializer(work_experinece, many=True)
            
            # get user profile
            serializer_profile = BaseProfileSerializer(queryset.user.user_profile)
            
            # get number of tasks related to cases from Task Model
            tasks = Task.objects.filter(case=queryset).count()
            
            data = {
                "case_details" : serializer_cases.data,
                "user_qualifications" : serializer_qua.data,
                "user_work_experience" : serializer_work.data,
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

class UpdateCaseProgramView(GenericViewSet):
    serializer_class = CaseProgramSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_all_programs(self, request):
        response = {'status':1, 'message':'All programs retreived', 'data':''}
        queryset = Program.objects.all()
        serializer = BaseCaseProgramSerializer(queryset, many=True)
        response['data'] = serializer.data
        return Response(response)

    def update_program(self, request, **kwargs):
        response = {'status':1, 'message':'Program Updated successfully', 'data':''}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        program = serializer.validated_data
        case_id = kwargs.get('case_id')
        user_id = request.user.id

        # check case id belongs to request.user and return case obj
        case_serializer = CaseIDSerializer(data = {"case_id": case_id,"user_id": user_id})
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data
        
        try:
            #get case obj
            case = Case.objects.get(case_id=case_obj)
            case.program = program
            case.save()
        except Case.DoesNotExist as e:
            logger.error('ERROR: CASE:UpdateCaseProgramView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error('ERROR: CASE:UpdateCaseProgramView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        case_serializer = CasesSerializer(case)
        response['data'] = case_serializer.data
        return Response(response)