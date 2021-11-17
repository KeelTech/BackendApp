from django.urls import path
from django.conf.urls import url
from .views import ChatList

urlpatterns = [
    path('list/<str:case_id>', ChatList.as_view({'get' : 'listChats'}), name='list-chat'),
    path('create', ChatList.as_view({'post' : 'createChat'}), name='create-chat'),
    path('unread-chats', ChatList.as_view({'get' : 'get_unread_messages'}), name='unread-chats'),
]
