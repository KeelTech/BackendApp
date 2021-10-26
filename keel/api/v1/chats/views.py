from django.core.checks import messages
from django.db.models import Q

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status as HTTP_STATUS
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
# from rest_framework.pagination import LimitOffsetPagination

from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error, logging_format
from keel.Core.constants import GENERIC_ERROR, LOGGER_MODERATE_SEVERITY
from keel.chats.models import Chat, ChatReceipts, ChatRoom

from keel.api.v1.cases.serializers import CaseIDSerializer

from .serializers import ChatCreateSerializer, ChatRoomSerializer, BaseChatListSerializer, ChatReceiptsSerializer
from .pagination import ChatsPagination, CHAT_PAGINATION_LIMIT


class ChatList(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def chat_receipt(self, user, case, chat):
        serializer = ChatReceiptsSerializer(data={"case_id":case, "user_id":user, "chat_id":chat, "read":True})
        serializer.is_valid(raise_exception=True)
        try:
            ChatReceipts.objects.filter(user_id=user, case_id=case).delete()
            serializer.save()
        except Exception as e:
            log_error("INFO", "ChatList: chat_receipt", str(user), err = str(e), msg = "An error occured", case_id = case)

    def listChats(self, request, format = 'json', **kwargs):

        response = {
            "status" : 0,
            "message" : "Chat list is fetched successfully",
            "data" : [],
        }

        user = request.user
        user_id = user.id

        case_id = kwargs.get("case_id","")
            
        # validate Case ID against User/Agent
        case_serializer = CaseIDSerializer(data = {"case_id": case_id, "user_id": user_id})
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        try:
            chat_room = ChatRoom.objects.filter(Q(user = user_id) | Q(agent = user_id)).get(case = case_id)
        except ChatRoom.DoesNotExist as e:
            log_error("INFO", "ChatList: listChats", str(user_id), err = str(e), msg = "invalid case_id", case_id = case_id)

            # if not found create ChatRoom between user and agents
            chat_room_serializer = ChatRoomSerializer(data = {'user': case_obj.user_id, 'agent': case_obj.agent_id, 'case': case_id})
            chat_room_serializer.is_valid(raise_exception = True)
            chat_room = chat_room_serializer.save()

        pagination_class = ChatsPagination()

        queryset = Chat.objects.filter(chatroom = chat_room).order_by("-id")
        paginate_queryset = pagination_class.paginate_queryset(queryset, request)
        serializer_class = BaseChatListSerializer(paginate_queryset, many = True)
        resp_data = dict(pagination_class.get_paginated_response(serializer_class.data).data)

        # read receipt for chat
        if len(queryset) > 0:
            receipt = self.chat_receipt(user_id, case_id, queryset[0].pk)

        response["data"] = resp_data
        response["requested_by"] = user_id
        return Response(response, status = HTTP_STATUS.HTTP_200_OK)


    def createChat(self, request, format = 'json'):

        response = {
            "status" : 0,
            "message" : "Chat created successfully",
            "data" : [],
        }

        user = request.user
        user_id = user.id

        req_data = request.data
        case_id = req_data.get("case_id", "")
        
        try:
            chat_room = ChatRoom.objects.filter(Q(user = user_id) | Q(agent = user_id)).get(case = case_id)
        except ChatRoom.DoesNotExist as e:
            log_error("ERROR", "ChatList: createChat", str(user_id), err = str(e), msg = "invalid case_id", case_id = case_id)
            response["status"] = 1
            response["message"] = "Invalid Request"
            return Response(response, status = HTTP_STATUS.HTTP_400_BAD_REQUEST)

        req_data["chatroom"] = chat_room.id
        req_data["sender"] = user.id

        serializer_class = ChatCreateSerializer(data = req_data)
        serializer_class.is_valid(raise_exception = True)

        try:
            validated_data = serializer_class.validated_data
            chat_obj = serializer_class.create(validated_data)
            queryset = Chat.objects.filter(chatroom = chat_room).order_by("-created_at")[:CHAT_PAGINATION_LIMIT]
            response['data'] = ChatCreateSerializer(queryset, many = True).data
        except Exception as e:
            log_error("ERROR","ChatList: createChat", str(user_id), err = str(e), msg = "Validation/serializer error")
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            return Response(response, status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status = HTTP_STATUS.HTTP_200_OK)

    def get_unread_messages(self, request):
        response = {'status':1, 'message':'Number of unread messages for user', 'data':''}
        
        try:
            user_messages = ChatReceipts.objects.filter(user_id=request.user.id).last()
        except ChatReceipts.DoesNotExist as err:
            log_error(LOGGER_MODERATE_SEVERITY, "ChatList:get_unread_messages", request.user.id, 
                            description=str(err))
            response["message"] = str(err)
            return Response(response, status=HTTP_STATUS.HTTP_404_NOT_FOUND)
        
        if user_messages is None:
            chat_id = 0
        else:
            chat_id = user_messages.chat_id.id
        
        # user case
        try:
            user_case = request.user.users_cases.get(user=request.user)
            case_chat = ChatRoom.objects.get(case=user_case)
            chats = Chat.objects.filter(chatroom=case_chat).exclude(sender=request.user).last()
            if chats is None:
                messages_for_case = chat_id
            else:
                messages_for_case = chats.id
        except Exception as err:
            log_error(LOGGER_MODERATE_SEVERITY, "ChatList:get_unread_messages", request.user.id, 
                            description=str(err))
            response["message"] = str(err)
            return Response(response, status=HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # number of unread messages
        unread_message = messages_for_case - chat_id
        response["data"] = unread_message
        return Response(response)