import logging

from keel.cases.models import Case
from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import (GENERIC_ERROR, LOGGER_CRITICAL_SEVERITY,
                                 LOGGER_LOW_SEVERITY, LOGGER_MODERATE_SEVERITY)
from keel.Core.err_log import logging_format
from rest_framework import serializers

from .utils import extract_user_details

logger = logging.getLogger('app-logger')

class BaseChatListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField("get_sender_name")

    class Meta:
        model = Chat
        fields = ('id','sender', 'sender_name', 'chatroom','message','created_at')
    
    def get_sender_name(self, obj):
        user = extract_user_details(obj.sender)
        return user

class ChatCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chat
        fields = ('id','sender','chatroom','message','created_at')

    def create(self, validated_data):
        try:
            chat_obj = Chat.objects.create(**validated_data)
        except Exception as err:
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "ChatCreateSerializer:create"),
                "", description=str(err))
            raise serializers.ValidationError("Failed to create chat object")
        return chat_obj

class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def create(self, validated_data):
        try:
            chat_room_obj = ChatRoom.objects.create(**validated_data)
        except Exception as err:
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "ChatRoomSerializer:create"),
                "", description=str(err))
            raise serializers.ValidationError("Failed to create chat room object")
        return chat_room_obj

class ChatReceiptsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatReceipts
        fields = ('chat_id', 'case_id', 'user_id', 'read')
