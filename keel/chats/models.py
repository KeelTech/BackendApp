from django.conf import settings
from django.db import models
from keel.authentication.models import User
from keel.cases.models import Case
from keel.Core.models import SoftDeleteModel, TimeStampedModel

# Create your models here.

class ChatRoom(TimeStampedModel, SoftDeleteModel):

    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_chatrooms')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_chatrooms')
    case = models.ForeignKey(Case,on_delete=models.deletion.DO_NOTHING, related_name='cases_chatrooms') 


class Chat(TimeStampedModel, SoftDeleteModel):

    sender = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='sender_chats')
    message = models.TextField(null=True, blank=True)
    chatroom = models.ForeignKey(ChatRoom,on_delete=models.deletion.DO_NOTHING, related_name='chatroom_chats') 


class ChatReceipts(TimeStampedModel, SoftDeleteModel):

    chat_id = models.ForeignKey(Chat, on_delete=models.DO_NOTHING, related_name="chat_receipts")
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="user_chat_receipts")
    case_id = models.ForeignKey(Case, on_delete=models.DO_NOTHING, related_name="case_chats_receipts")
    read = models.BooleanField(default=False)
