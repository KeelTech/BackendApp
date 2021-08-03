
from rest_framework import serializers


class SingleSchedulingLinkBookingUrlSerializer(serializers.Serializer):
    booking_url = serializers.CharField()


class SingleSchedulingLinkSerializer(serializers.Serializer):
    details = SingleSchedulingLinkBookingUrlSerializer()
    pass
