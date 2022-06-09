from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class StudentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)

        # get insensitive email match
        user = User.objects.filter(email__iexact=email).first()

        if not user and not user.check_password(password) and not user.is_active:
            raise serializers.ValidationError("Invalid Credentials, Try Again")

        # check user type
        if user.user_type != user.STUDENT:
            raise serializers.ValidationError("Not a customer account")

        return user
