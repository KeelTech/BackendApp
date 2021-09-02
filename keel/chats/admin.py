from enum import auto
from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Chat, ChatRoom

class ChatAdmin(CustomBaseModelAdmin):
    autocomplete_fields = ('sender', )

class ChatRoomAdmin(CustomBaseModelAdmin):
    autocomplete_fields = ('user', 'agent', 'case')


admin.site.register(Chat, ChatAdmin)
admin.site.register(ChatRoom, ChatRoomAdmin)