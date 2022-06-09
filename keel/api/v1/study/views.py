from django.contrib.auth import get_user_model
from keel.api.v1.auth import serializers
from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import CustomToken
from keel.authentication.models import User as user_model
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY
from keel.Core.err_log import log_error
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .serializers import StudentLoginSerializer

User = get_user_model()


class StudyStudentViewset(viewsets.GenericViewSet):

    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def student_signup(self, request, format="json"):
        response = {"status": 1, "message": ""}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data[
            "user_type"
        ] = user_model.STUDENT  # add user type to validated data

        try:
            user = self.create(validated_data)
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(
                user=user, token=token_to_save["token"]
            )
        except Exception as e:
            log_error(
                LOGGER_CRITICAL_SEVERITY,
                "StudyStudentViewset:student_signup",
                "",
                description="Student sign up failed",
            )
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "email": obj.user.email,
            "token": obj.token,
        }
        response["message"] = data
        return Response(response, status=status.HTTP_200_OK)


class StudyStudentLoginViewset(viewsets.GenericViewSet):
    serializer_class = StudentLoginSerializer

    def student_login(self, request, format="json"):
        response = {"status": 1, "message": ""}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        try:
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(
                user=user, token=token_to_save["token"]
            )
        except Exception as e:
            log_error(
                LOGGER_CRITICAL_SEVERITY,
                "StudyStudentViewset:student_signup",
                "",
                description="Student sign up failed",
            )
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = {
            "email": obj.user.email,
            "token": obj.token,
        }
        response["message"] = data
        return Response(response, status=status.HTTP_200_OK)
