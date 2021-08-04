from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.template.loader import get_template

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import ScheduleCallSerializer
from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import User
from keel.calendly.utils import calendly_business_logic
from keel.call_schedule.models import CallSchedule

import logging
logger = logging.getLogger('app-logger')


class ScheduleCallViewSet(GenericViewSet):

    def get_schedule_page(self, request, **kwargs):
        template = get_template('calendly_landing.html')  # getting our templates
        return HttpResponse(template.render())


class RCICScheduleUrl(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_call_schedule_url(self, request, **kwargs):
        response = {
            'status': 1,
            "message": ''
        }
        try:
            user = request.user
            rcic_email = user.users_cases.get(is_active=True).agent.email
        except ObjectDoesNotExist as err:
            response["status"] = 0
            response["message"] = "Case does not exist for the user"
            return Response(response, status.HTTP_400_BAD_REQUEST)
        except MultipleObjectsReturned as err:
            response["status"] = 0
            response["message"] = "Multiple RCIC assigned to the user"
            return Response(response, status.HTTP_400_BAD_REQUEST)
        schedule_url = calendly_business_logic.get_agent_schedule_url(user.first_name, user.email, rcic_email)

        if not schedule_url:
            response["status"] = 0
            response["message"] = "Error getting schedule url of assigned RCIC"
            return Response(response, status.HTTP_400_BAD_REQUEST)

        response["message"] = {"schedule_url": schedule_url}
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
        try:
            host_user = User.objects.get(pk=validated_data["host_user_id"])
        except Exception as err:
            response["status"] = 0
            response["message"] = "Invalid host id"
            return Response(response, status.HTTP_400_BAD_REQUEST)

        event_details = calendly_business_logic.create_event_schedule(
            request.user, host_user, validated_data["calendly_schdule_event_url"])

        if not event_details["status"]:
            response["status"] = 0
            response["message"] = "Error while creating schedule Id"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["message"] = event_details["data"]

        return Response(response, status.HTTP_200_OK)

    def reschedule_call(self, request, **kwargs):
        response = {
            "status": 0,
            "message": ""
        }
        schedule_id = kwargs["schedule_id"]
        serializer = ScheduleCallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        schedule_obj_list = CallSchedule.objects.filter(
            visitor_user=request.user, pk=schedule_id, is_active=True,
            status__in=(CallSchedule.ACTIVE, CallSchedule.RESCHEDULED))
        if not schedule_obj_list or len(schedule_obj_list) > 1:
            if not schedule_obj_list:
                response["message"] = "Error getting schedule with this id and associated user which is in" \
                                      "active or rescheduled status"
            else:
                response["message"] = "Getting more than one schedule with this id and associated " \
                                      "user which is in active or rescheduled status"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        reschedule_details = calendly_business_logic.reschedule_scheduled_event(schedule_obj_list[0],
                                                                                validated_data.calendly_schedule_event_url)
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
        schedule_obj_list = CallSchedule.objects.filter(
            visitor_user=request.user, pk=schedule_id, is_active=True,
            status__in=(CallSchedule.ACTIVE, CallSchedule.RESCHEDULED))
        if not schedule_obj_list or len(schedule_obj_list) > 1:
            if not schedule_obj_list:
                response["message"] = "Error getting schedule with this id and associated user which is in" \
                                      "active or rescheduled status"
            else:
                response["message"] = "Getting more than one schedule with this id and associated " \
                                      "user which is in active or rescheduled status"
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        calendly_business_logic.cancel_scheduled_event(schedule_obj_list[0])

        return Response(response, status.HTTP_200_OK)

