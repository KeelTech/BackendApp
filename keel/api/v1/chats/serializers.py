from rest_framework import serializers
from keel.chats.models import Chat, ChatRoom 
from keel.cases.models import Case

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


