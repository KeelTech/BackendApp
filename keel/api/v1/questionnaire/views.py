from keel.authentication.backends import JWTAuthentication
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.questionnaire.models import Question, SpouseQuestion
from rest_framework import response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from keel.api.v1.eligibility_calculator.helpers import crs_calculator
from .serializers import (
    AnsweredQuestionSerializer,
    QuestionSerializer,
    SpouseQuestionSerializer,
    QuestionnaireAnalysisSerializer,
)


class QuestionViewSet(GenericViewSet):
    serializer_class = QuestionSerializer

    def get_questions(self, request):
        response = {
            "status": 1,
            "message": "questions retrieved successfully",
            "data": "",
        }
        query_params = request.query_params.get("is_active", None)

        try:
            # filter by is_active if query_params is true
            if query_params == "true":
                questions = Question.objects.filter(is_active=True)

            # if query_params is false, get all questions
            else:
                questions = Question.objects.all()

            serializer = QuestionSerializer(questions, many=True).data

            spouse_question_queryset = SpouseQuestion.objects.all()
            spouse_question_serializer = SpouseQuestionSerializer(
                spouse_question_queryset, many=True
            ).data

        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionViewSet:get_questions",
                request.user.id,
                description="Failed to get questionnaires",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response["data"] = {
            "questions": serializer,
            "spouse_questions": spouse_question_serializer,
        }
        return Response(response)


class QuestionnarieViewSet(GenericViewSet):
    serializer_class = AnsweredQuestionSerializer

    def submit_questionnaire(self, request):
        response = {
            "status": 1,
            "message": "questionnaire submitted successfully",
            "data": "",
        }

        data = request.data

        email = data.get("email", None)
        spouse_exist = data.get("spouse_exist", None)
        age = data.get("age", None)
        education = data.get("education", None)
        language = {
            "first_language_speaking": data.get("first_language_speaking", None),
            "first_language_reading": data.get("first_language_reading", None),
            "first_language_writing": data.get("first_language_writing", None),
            "first_language_listening": data.get("first_language_listening", None),
            "second_language_speaking": data.get("second_language_speaking", None),
            "second_language_reading": data.get("second_language_reading", None),
            "second_language_writing": data.get("second_language_writing", None),
            "second_language_listening": data.get("second_language_listening", None),
        }
        work_experience = data.get("work_experience", None)
        spouse_details = {
            "spouse_education": data.get("spouse_education", None),
            "spouse_language_speaking": data.get("spouse_language_speaking", None),
            "spouse_language_writing": data.get("spouse_language_writing", None),
            "spouse_language_listening": data.get("spouse_language_listening", None),
            "spouse_language_reading": data.get("spouse_language_reading", None),
            "spouse_work_experience": data.get("spouse_work_experience", None),
        }
        arranged_employement = data.get("arranged_employement", None)
        relative_in_canada = data.get("relative_in_canada", None)
        provincial_nomination = data.get("provincial_nomination", None)

        try:

            if spouse_exist == "true" or spouse_exist == "Yes":

                # instantiate crs calculator
                crs_calc = crs_calculator.CrsCalculator(
                    age,
                    education,
                    language,
                    work_experience,
                    spouse_details,
                    arranged_employement,
                    relative_in_canada,
                    provincial_nomination,
                )
                crs_score = crs_calc.calculate_crs_with_spouse()

            elif spouse_exist == "false" or spouse_exist == "No":

                # instantiate crs calculator
                crs_calc = crs_calculator.CrsCalculator(
                    age,
                    education,
                    language,
                    work_experience,
                    spouse_details,
                    arranged_employement,
                    relative_in_canada,
                    provincial_nomination,
                )
                crs_score = crs_calc.calculate_crs_without_spouse()

            else:
                response["message"] = "Return 'spouse_exist' key in payload"
                response["status"] = 0
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionViewSet:get_questions",
                request.user.id,
                description="Failed to get questionnaires",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # send email for crs score

        response["data"] = "Crs score {}".format(crs_score)
        return Response(response)


class QuestionAnalysisViewSet(GenericViewSet):

    serializer_class = QuestionnaireAnalysisSerializer
    
    def create_analysis(self, request):
        response = {"status":1, "message":"analysis created successfully", "data":""}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionAnalysisViewSet:create_analysis",
                "",
                description="Failed to create analysis",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(response)