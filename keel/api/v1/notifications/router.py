from django.urls import path
from .views import NotificationViews


urlpatterns = [
    path('get-notifications', NotificationViews.as_view({'get' : 'get_notifications'}), name="get-notifications"),
    path('mark-notification/<int:pk>', NotificationViews.as_view({'post' : 'mark_notification_read'}), name="mark_notification_read"),
]