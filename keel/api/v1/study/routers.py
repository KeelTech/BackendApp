from django.urls import path

from .views import StudyStudentViewset, StudyStudentLoginViewset

urlpatterns = [
    path(
        "student-signup",
        StudyStudentViewset.as_view({"post": "student_signup"}),
        name="student-signup",
    ),
    path(
        "student-login",
        StudyStudentLoginViewset.as_view({"post": "student_login"}),
        name="student-login",
    ),
]
