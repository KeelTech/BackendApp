from keel.payment.models import UserOrderDetails
from rest_framework import serializers


class UserOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrderDetails
        fields = ["id", "first_name", "last_name", "phone_number", "email"]
