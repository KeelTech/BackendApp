from keel.chats.models import Chat, ChatReceipts, ChatRoom
from keel.Core.constants import LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import log_error


class UnreadChats(object):
    
    def get_unread_messages(obj):
        chat_receipts = obj.case_chats_receipts.all()
        user = obj.user
        last_chat = obj.cases_chatrooms.all()
        try:
            if len(chat_receipts) > 0:
                user_messages = chat_receipts[len(chat_receipts) - 1] if chat_receipts else None
            else:
                user_messages = None
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
            if len(last_chat) > 0:
                chats = last_chat[len(last_chat) -1] if last_chat else None
            else:
                chats = None
            
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
