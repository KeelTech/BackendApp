from rest_framework import serializers
from keel.notifications.models import InAppNotification
from keel.api.v1.auth.serializers import UserSerializer


class InAppNotificationSerializer(serializers.ModelSerializer):
    # user_id = serializers.SerializerMethodField()

    class Meta:
        model = InAppNotification
        fields = ('id', 'text', 'seen', 'user_id', 'case_id', 'category')
    
    # def get_user_id(self, obj):
    #     return obj.user_id.email