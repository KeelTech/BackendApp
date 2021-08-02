from django.urls import path
from django.conf.urls import url
from .views import ChatList

urlpatterns = [
    path('list/<int:id>', ChatList.as_view({'get' : 'listChats'}), name='list-chat'),
    path('create', ChatList.as_view({'post' : 'createChat'}), name='create-chat'),
]
