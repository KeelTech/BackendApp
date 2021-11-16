from rest_framework import views
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import OptionSerializer, QuestionSerializer
from keel.questionnaire.models import Question, Option


class QuestionViewSet(GenericViewSet):
    serializer_class = QuestionSerializer

    def get_questions(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)