from django.urls import path
from .views import NotificationViews


urlpatterns = [
    path('get-notifications', NotificationViews.as_view({'get' : 'get_notifications'}), name="get-notifications"),
]