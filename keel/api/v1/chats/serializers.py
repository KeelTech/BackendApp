from rest_framework import serializers
from keel.chats.models import Chat, ChatRoom 
from keel.cases.models import Case
from .utils import extract_user_details


class BaseChatListSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField("get_sender")

    class Meta:
        model = Chat
        fields = ('id','sender','chatroom','message','created_at')
    
    def get_sender(self, obj):
        user = extract_user_details(obj.sender)
        return user

class ChatCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chat
        fields = ('id','sender','chatroom','message','created_at')

    def create(self, validated_data):
        chat_obj = Chat.objects.create(**validated_data)
        return chat_obj

class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = "__all__"

    def create(self, validated_data):

        chat_room_obj = ChatRoom.objects.create(**validated_data)
        return chat_room_obj


