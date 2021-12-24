from django.urls import path
from .views import QuestionViewSet, QuestionnarieViewSet, QuestionAnalysisViewSet

urlpatterns = [
    path('get-questions', QuestionViewSet.as_view({'get':'get_questions'}), name="get_questions"),
    path('submit-questionnaires', QuestionnarieViewSet.as_view({'post':'submit_questionnaire'}), name="submit_questionnaire"),
    path('create-analysis', QuestionAnalysisViewSet.as_view({'post':'create_analysis'}), name="create_analysis"),
]
