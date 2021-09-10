from django.urls import path

from .views import OrderViewSet, WebHookViewSet

urlpatterns = [
    path("create/order/", OrderViewSet.as_view({"post": "create"})),
    path("webhook/", WebHookViewSet.as_view({"post": "process_event"})),
]
