from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error


class UnreadChats(object):
    
    def get_unread_messages(user):
        try:
            user_messages = ChatReceipts.objects.filter(user_id=user.id).last()
        except ChatReceipts.DoesNotExist as err:
            log_error(LOGGER_MODERATE_SEVERITY, "ChatList:get_unread_messages", user.id, 
                            description=str(err))
            return "An error occured, check logs for details"
        
        if user_messages is None:
            chat_id = 0
        else:
            chat_id = user_messages.chat_id.id

        # user case
        try:
            user_case = user.users_cases.get(user=user)
            case_chat = ChatRoom.objects.get(case=user_case)
            chats = Chat.objects.filter(chatroom=case_chat).exclude(sender=user).last()
            if chats is None:
                messages_for_case = chat_id
            else:
                messages_for_case = chats.id
        except Exception as err:
            log_error(LOGGER_MODERATE_SEVERITY, "ChatList:get_unread_messages", user.id, 
                            description=str(err))
            return "An error occured, check logs for details"
        
        # number of unread messages
        unread_message = messages_for_case - chat_id
        return unread_message
