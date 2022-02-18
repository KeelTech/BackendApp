from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error


class UnreadChats(object):

    def __init__(self, obj):
        self.obj = obj

    def queryset_sort(self, queryset, user):
        """
        To get the unread chats for the user
        We filter the Chat Receipts by case to get the last read message 
        and the chat to get the last sent message
        """
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
        user = self.obj
        # chats = Chats.objects.filter(
        # print(self.obj.cases_chatrooms__chatroom_chats.all())
        # chat = [p for p in self.obj.cases_chatrooms__chatroom_chats]

        return 0