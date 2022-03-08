from keel.authentication.backends import JWTAuthentication
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.questionnaire.models import DropDownModel, Question, SpouseQuestion
from rest_framework import response, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from keel.api.v1.questionnaire.helper.answer_dict import AnswerDict
from keel.api.v1.auth.helpers.email_helper import send_crs_score

from keel.api.v1.eligibility_calculator.helpers import (
    crs_calculator,
    crs_calculator_without_spouse,
    crs_calculator_with_spouse,
)
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
                questions = (
                    Question.objects.prefetch_related(
                        "question_checkbox",
                        "question_dropdown",
                        "dependent_question_checkbox",
                        "dependent_question_dropdown",
                    )
                    .filter(is_active=True)
                    .order_by("index")
                )

            # if query_params is false, get all questions
            else:
                questions = Question.objects.prefetch_related(
                    "question_checkbox",
                    "question_dropdown",
                    "dependent_question_checkbox",
                    "dependent_question_dropdown",
                ).all()

            serializer = QuestionSerializer(questions, many=True).data

        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionViewSet:get_questions",
                "",
                description="Failed to get questionnaires",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        response["data"] = {
            "questions": serializer,
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

        try:
            spouse_exist = data.get("spouse_exist", None)

            if spouse_exist:
                answer_id = spouse_exist.get("answer_id", None)
                spouse_answer = DropDownModel.objects.get(id=answer_id)
                spouse_exist = spouse_answer.dropdown_text

                if spouse_exist == "true" or spouse_exist == "Yes":
                    crs = crs_calculator_with_spouse.CrsCalculatorWithSpouse(data)
                    crs_score = crs.calc_score()

            else:
                crs = crs_calculator_without_spouse.CrsCalculatorWithoutSpouse(data)
                crs_score = crs.calc_score()

        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionnarieViewSet:submit_questionnaire",
                "",
                description="Failed to calculate crs",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # send email for crs score
        try:
            context = {
                "score": crs_score,
            }
            send_crs_score(context, email)
        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "QuestionnarieViewSet:submit_questionnaire",
                "",
                description="Failed to send crs score email",
            )

        response["data"] = "Crs score {}".format(crs_score)
        return Response(response)


class QuestionAnalysisViewSet(GenericViewSet):

    serializer_class = QuestionnaireAnalysisSerializer

    def create_analysis(self, request):
        response = {"status": 1, "message": "analysis created successfully", "data": ""}
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
