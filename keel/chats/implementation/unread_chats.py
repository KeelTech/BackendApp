from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error


class UnreadChats(object):
    def user_unread_messages(obj):
        user = obj.user
        try:
            user_messages2 = obj.case_chats_receipts.all()
            if len(user_messages2) > 0:
                user_messages = user_messages2[len(user_messages2)-1] if user_messages2 else None
            else:
                user_messages = None

            # user_messages = ChatReceipts.objects.filter(user_id=user).last()
        except ChatReceipts.DoesNotExist as err:
            log_error(
                LOGGER_MODERATE_SEVERITY,
                "UnreadChats:user_unread_messages",
                user.id,
                description=str(err),
            )
            return "An error occured, check logs for details"

        if user_messages is None:
            chat_id = 0
        else:
            chat_id = user_messages.chat_id.id

        # user case
        try:
            chat_room2 = obj.cases_chatrooms.all()
            if len(chat_room2) > 0:
                chat_room = chat_room2[len(chat_room2)-1] if chat_room2 else None
            else:
                chat_room = None
            
            # chat_room = ChatRoom.objects.get(case=obj)
            if chat_room is None:
                chats = None
            else:
                chats = chat_room.chatroom_chats.all()
                chats = chats[len(chats)-1] if chats else None

            if chats is None:
                messages_for_case = chat_id
            else:
                messages_for_case = chats.id
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

    # def 