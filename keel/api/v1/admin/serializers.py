from rest_framework import serializers


class AgentVerificationSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=1000000000,max_value=9999999999)
    user_type = serializers.IntegerField(min_value=2,max_value=3)
