from keel.payment.models import UserOrderDetails
from rest_framework import serializers
from keel.plans.implementation.plan_util_helper import get_plan_instance_with_id


class UserOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOrderDetails
        fields = ["id", "first_name", "last_name", "phone_number", "email", "plan_id"]


class RazorpayCaptureserializer(serializers.Serializer):
    payment_id = serializers.CharField(max_length=100)
    transaction_id = serializers.CharField(max_length=100)
    order_id = serializers.CharField(max_length=100)
