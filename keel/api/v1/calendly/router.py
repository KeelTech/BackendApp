from django.urls import path
from .views import ScheduleCallViewSet, RCICScheduleUrl, CallScheduleViewSet

urlpatterns = [
    path("page", ScheduleCallViewSet.as_view({"get": "get_schedule_page"})),
    path("agent/schedule-url", RCICScheduleUrl.as_view({"get": "get_call_schedule_url"})),
    path("agent/schedule-call", CallScheduleViewSet.as_view({"post": "create_call_schedule"})),
    path("reschedule-call/<str:schedule_id>", CallScheduleViewSet.as_view({"post": "reschedule_call"})),
    path("cancel-call/<str:schedule_id>", CallScheduleViewSet.as_view({"post": "cancel_scheduled_call"})),
    path("active-schedule/details", CallScheduleViewSet.as_view({"get": "get_scheduled_call"})),
]

