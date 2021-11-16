from django.urls import path
from .views import QuestionViewSet

urlpatterns = [
    path('get-questions', QuestionViewSet.as_view({'get':'get_questions'}), name="get_questions"),
]
