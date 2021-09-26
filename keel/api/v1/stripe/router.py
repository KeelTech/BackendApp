from django.urls import path

from .views import WebHookViewSet

urlpatterns = [
    path("webhook", WebHookViewSet.as_view({"post": "process_event"})),
]
