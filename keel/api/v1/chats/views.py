from django.db.models import Q

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status as HTTP_STATUS
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
# from rest_framework.pagination import LimitOffsetPagination

from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error
from keel.Core.constants import GENERIC_ERROR
from keel.chats.models import Chat, ChatRoom

from keel.api.v1.cases.serializers import CaseIDSerializer

from .serializers import ChatCreateSerializer, ChatRoomSerializer
from .pagination import ChatsPagination, CHAT_PAGINATION_LIMIT


class ChatList(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

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
        serializer_class = ChatCreateSerializer(paginate_queryset, many = True)
        resp_data = dict(pagination_class.get_paginated_response(serializer_class.data).data)

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



