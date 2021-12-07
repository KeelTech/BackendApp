import requests
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import ScheduleCallSerializer
from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import User
from keel.calendly.utils import calendly_schedule_manager, is_valid_webhook_signature
from keel.calendly.constants import CALENDLY_WEBHOOK_PATH, CALENDLY_WEBHOOK_SIGNATURE_KEY, CALENDLY_WEBHOOK_EVENTS
from keel.call_schedule.implementation.schedule_manager import CallScheduleManager
from keel.call_schedule.models import CallSchedule
from keel.calendly.models import CalendlyCallSchedule
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_MODERATE_SEVERITY
from keel.Core.err_log import logging_format

import logging
logger = logging.getLogger('app-logger')


class ScheduleCallViewSet(GenericViewSet):

    def get_schedule_page(self, request, **kwargs):
        template = get_template('calendly_landing.html')  # getting our templates
        return HttpResponse(template.render())


class ScheduleUrl(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_call_schedule_url(self, request, **kwargs):
        response = {
            'status': 1,
            "message": ''
        }
        schedule_manager = CallScheduleManager(request.user.pk, CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT)
        schedule_url_response = schedule_manager.generate_schedule_url()
        if not schedule_url_response["status"]:
            response["status"] = 0
            response["message"] = schedule_url_response["error"]
            return Response(response, status.HTTP_400_BAD_REQUEST)

        response["message"] = {"schedule_url": schedule_url_response["schedule_url"]}
        return Response(response, status=status.HTTP_200_OK)


class CallScheduleViewSet(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def create_call_schedule(self, request, **kwargs):
        response = {
            "status": 1,
            "message": ""
        }
        serializer = ScheduleCallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        call_schedule_manager = CallScheduleManager(request.user.pk, CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT)
        event_details = call_schedule_manager.create_schedule(validated_data["calendly_invitee_url"])
        if not event_details["status"]:
            response["status"] = 0
            response["message"] = "Error while creating schedule Id"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["message"] = event_details["data"]

        return Response(response, status.HTTP_200_OK)

    def CallScheduleViewSet(self, request, **kwargs):
        response = {
            "status": 0,
            "message": ""
        }
        schedule_id = kwargs["schedule_id"]

        try:
            schedule_obj = CallSchedule.objects.get(
                visitor_user=request.user, pk=schedule_id, is_active=True,
                status__in=(CallSchedule.ACTIVE, CallSchedule.RESCHEDULED))
        except ObjectDoesNotExist as err:
            logger.error(logging_format(LOGGER_MODERATE_SEVERITY, "CallScheduleViewSet:CallScheduleViewSet"),
                "", description=str(err))
            response["message"] = "Error getting schedule with this id and associated user which is in" \
                                  "active or rescheduled status"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        reschedule_details = calendly_schedule_manager.cancel_reschedule_scheduled_event(schedule_obj)
        if not reschedule_details["status"]:
            response["message"] = reschedule_details["error"]
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["status"] = 1
        response["message"] = "Reschedule successful"

        return Response(response, status.HTTP_200_OK)

    def cancel_scheduled_call(self, request, **kwargs):
        response = {
            "status": 0,
            "message": ""
        }
        schedule_id = kwargs["schedule_id"]
        try:
            schedule_obj = CallSchedule.objects.get(
                visitor_user=request.user, pk=schedule_id, is_active=True,
                status__in=(CallSchedule.ACTIVE, CallSchedule.RESCHEDULED))
        except ObjectDoesNotExist as err:
            logger.error(logging_format(LOGGER_MODERATE_SEVERITY, "CallScheduleViewSet:cancel_scheduled_call"),
                "", description=str(err))
            response["message"] = "Error getting schedule with this id and associated user which is in" \
                                      "active or rescheduled status"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        calendly_schedule_manager.cancel_reschedule_scheduled_event(schedule_obj)

        return Response(response, status.HTTP_200_OK)

    def get_scheduled_call(self, request, **kwargs):
        response = {
            "status": 0,
            "message": ""
        }

        call_schedule_manager = CallScheduleManager(request.user.pk, CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT)
        schedules = call_schedule_manager.get_schedules()
        if not schedules["status"]:
            response["message"] = schedules["error"]
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["status"] = 1
        response["message"] = schedules["data"]
        return Response(response, status.HTTP_200_OK)


class WebHookViewSets(GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def subscribe(self, request, **kwargs):
        response = {
            "status": 0,
            "message": ""
        }
        if not request.user.is_superuser:
            return Response("User is not a superuser", status.HTTP_400_BAD_REQUEST)
        url = settings.CALENDLY_BASE_URL + CALENDLY_WEBHOOK_PATH
        payload = {
            "url": settings.BASE_URL + reverse("calendly_webhook_process_events"),
            "events": CALENDLY_WEBHOOK_EVENTS,
            "organization": settings.CALENDLY_ORGANIZATION_URL,
            "scope": "organization",
            "signing_key": settings.CALENDLY_SIGNING_KEY
        }
        headers = {
            "authorization": "Bearer " + settings.CALENDLY_PERSONAL_TOKEN
        }
        request_resp = requests.post(url=url, headers=headers, data=payload)
        status_code = request_resp.status_code
        if status_code == status.HTTP_201_CREATED:
            response["status"] = 1
            response["message"] = "Webhook created successfully"
            return Response(response, status.HTTP_200_OK)
        else:
            response["message"] = "Error creating webhook with status code - {}".format(status_code)
            return Response(response, status_code)


class WebHookProcessEvent(GenericViewSet):

    def process_event(self, request, **kwargs):
        response = {
            "status": 1,
            "error": "",
            "message": ""
        }

        if not is_valid_webhook_signature(request.headers.get(CALENDLY_WEBHOOK_SIGNATURE_KEY), request.data):
            response["error"] = "Invalid signature/body"
            response["status"] = 0
            return Response(response, status.HTTP_200_OK)

        schedule_manager = CallScheduleManager(request.user.pk, CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT)
        schedule_manager.webhook_process_event(request.data)
        return Response(response, status.HTTP_200_OK)
