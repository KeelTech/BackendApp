from django.urls import path
from .views import ScheduleCallViewSet, ScheduleUrl, CallScheduleViewSet, WebHookViewSets, WebHookProcessEvent

urlpatterns = [
    path("page", ScheduleCallViewSet.as_view({"get": "get_schedule_page"})),
    path("agent/schedule-url", ScheduleUrl.as_view({"get": "get_call_schedule_url"})),
    path("agent/schedule-call", CallScheduleViewSet.as_view({"post": "create_call_schedule"})),
    # path("reschedule-call/<str:schedule_id>", CallScheduleViewSet.as_view({"post": "reschedule_call"})),
    # path("cancel-call/<str:schedule_id>", CallScheduleViewSet.as_view({"post": "cancel_scheduled_call"})),
    path("active-schedule/details", CallScheduleViewSet.as_view({"get": "get_scheduled_call"})),
    path("webhook/subscribe", WebHookViewSets.as_view({"post": "subscribe"})),
    path("webhook/process-event", WebHookProcessEvent.as_view({"post": "process_event"}), name="calendly_webhook_process_events"),
]

