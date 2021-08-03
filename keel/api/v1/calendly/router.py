from django.urls import path
from .views import ScheduleCallViewSet, RCICScheduleUrl

urlpatterns = [
    path("page", ScheduleCallViewSet.as_view({"get": "get_schedule_page"})),
    path("schedule-url", RCICScheduleUrl.as_view({"get": "get_call_schedule_url"}))
]

