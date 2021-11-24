from keel.authentication.backends import JWTAuthentication
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.questionnaire.models import Question
from rest_framework import response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import QuestionSerializer


class QuestionViewSet(GenericViewSet):
    serializer_class = QuestionSerializer

    def get_questions(self, request):
        response = {'status' : 1, 'message' : 'questions retrieved successfully', 'data' : ''}
        try:
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True).data
        except Exception as e:
            log_error(LOGGER_LOW_SEVERITY, "QuestionViewSet:get_questions", request.user.id,
                    description="Failed to get questionnaires")
            response['status'] = 0
            response['message'] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        response['data'] = serializer
        return Response(response)
    

# class QuestionnarieViewSet(GenericViewSet):
#     serializer_class = AnsweredQuestionnairesSerializer
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JWTAuthentication,)

#     def submit_questionnaire(self, request):
#         response = {'status' : 1, 'message' : 'questionnaire submitted successfully', 'data' : ''}
#         answered_questionnaires = request.data.get('answered_questionnaires')
#         serializer = AnsweredQuestionnairesSerializer(data=answered_questionnaires, many=True)
#         serializer.is_valid(raise_exception=True)
#         for instance in serializer.validated_data:
#             instance['user'] = request.user
#         try:
#             serializer.save()
#         except Exception as e:
#             log_error(LOGGER_LOW_SEVERITY, "QuestionnarieViewSet:submit_questionnaire", request.user.id,
#                     description="Failed to submit questionnaires")
#             response['status'] = 0
#             response['message'] = str(e)
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
#         response['data'] = serializer.data
#         return Response(response)
