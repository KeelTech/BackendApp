from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error


class UnreadChats(object):

    def __init__(self, obj):
        self.obj = obj

    def queryset_sort(self, queryset, user):
        try:
            if len(queryset) > 0:
                return queryset[len(queryset)-1] if queryset else None
            else:
                return None
        except Exception as e:
            log_error(
                LOGGER_MODERATE_SEVERITY,
                "UnreadChats:queryset_sort",
                user.id,
                description=str(e),
            )
            return "An error occured, check logs for details"

    def user_unread_messages(self):
        user = self.obj.user

        try:
            queryset = self.obj.case_chats_receipts.all()
            user_messages = self.queryset_sort(queryset, user)
            chat_id = user_messages.chat_id.id if user_messages else 0
            
            queryset = self.obj.cases_chatrooms.all()
            chat_room = self.queryset_sort(queryset, user)
            
            if chat_room is None:
                chats = None
            else:
                queryset = chat_room.chatroom_chats.all()
                chats = self.queryset_sort(queryset, user)
            
            messages_for_case = chats.id if chats else chat_id

        except Exception as err:
            log_error(
                LOGGER_MODERATE_SEVERITY,
                "UnreadChats:user_unread_messages",
                user.id,
                description=str(err),
            )
            return "An error occured, check logs for details"

        # number of unread messages
        unread_message = messages_for_case - chat_id
        return unread_message