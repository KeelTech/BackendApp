import datetime
from dateutil import parser
import hashlib
import hmac
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduledUrl
from .apis import CalendlyApis
from .parser.webhook_data import CalendlyWebHookDataParser

from keel.calendly.constants import CALENDLY_SIGNATURE_VKEY, CALENDLY_SIGNATURE_TKEY, CALENDLY_EVENT_TOLERANCE_TIME
from keel.call_schedule.models import CallSchedule
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_LOW_SEVERITY
from keel.Core.err_log import logging_format

import logging
logger = logging.getLogger('app-logger')


class CalendlyScheduleManager(object):

    def _update_call_schedule(self, call_schedule_id, event_invitee_details):
        call_schedule_status = event_invitee_details["status"] if not event_invitee_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "start_time": event_invitee_details["start_time_utc"],
            "end_time": event_invitee_details["end_time_utc"],
            "status": call_schedule_status
        }
        calendly_call_schedule_details = {
            "invitee_url": event_invitee_details["event_invitee_url"],
            "cancel_url": event_invitee_details["cancel_url"],
            "reschedule_url": event_invitee_details["reschedule_url"],
            "communication_means": event_invitee_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.select_for_update().get(id=call_schedule_id).update(**call_schedule_details)
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule__id=call_schedule_id). \
                update(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    def _create_call_schedule(self, visitor_user_obj, host_user_obj, event_details):
        call_schedule_status = event_details["status"] if not event_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "visitor_user": visitor_user_obj,
            "host_user": host_user_obj,
            "start_time": event_details["start_time_utc"],
            "end_time": event_details["end_time_utc"],
            "status": call_schedule_status
        }
        calendly_call_schedule_details = {
            "invitee_url": event_details["invitee_url"],
            "cancel_url": event_details["cancel_url"],
            "reschedule_url": event_details["reschedule_url"],
            "communication_means": event_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.create(**call_schedule_details)
            calendly_call_schedule_details["call_schedule"] = call_schedule_obj
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.create(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    def _get_event_details(self, invitee_url):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        invitee_details = CalendlyApis.get_invitee_details(invitee_url)
        if not invitee_details["status"]:
            response["error"] = "Error in getting Invitee details"
            return response
        event_details = CalendlyApis.get_event_details(
            invitee_details["data"]["event_resource_url"])

        if not event_details["status"]:
            response["error"] = "Error in getting Event details"
            return response
        event_details["data"].update(invitee_details["data"])
        response["data"] = event_details["data"]
        response["status"] = 1
        return response

    def _is_active_event(self, event_details):
        if parser.parse(event_details["end_time_utc"]) <= timezone.now():
            return False
        if event_details["status"] == CallSchedule.CANCELED:
            return False
        return True

    def get_schedule_url(self, invitee_obj, host_user_obj):
        scheduling_url = None
        if not host_user_obj:
            err_msg = "No Host selected for the schedule of invitee - {}".format(invitee_obj.pk)
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "CalendlyScheduleManager:get_schedule_url",
                                        invitee_obj.pk, description=err_msg))
            return scheduling_url
        try:
            calendly_user_obj = CalendlyUsers.objects.get(user=host_user_obj)
        except ObjectDoesNotExist as err:
            message = "Error getting calendly user details for user {} " \
                      "with error {}".format(host_user_obj.email, err)
            logger.error(logging_format("", "CALENDLY-GET_AGENT_SCHEDULE_URL", "", description=message))
            return scheduling_url
        # event_resource_url = CalendlyApis.get_user_event_type(calendly_user_details.user_resource_url)
        if not calendly_user_obj.event_type_url:
            message = "Event resource url not present for the "\
                      "calendly user: {}".format(host_user_obj.email)
            logger.error(logging_format("", "CALENDLY-GET_AGENT_SCHEDULE_URL", "", description=message))
            return scheduling_url

        schedule_url_details = CalendlyApis.single_use_scheduling_link(
            calendly_user_obj.event_type_url, 1, invitee_obj.first_name, invitee_obj.email)

        if not schedule_url_details["status"]:
            return scheduling_url
        return schedule_url_details["schedule_url"]

    def create_event_schedule(self, visitor_user_obj, host_user_obj, invitee_url):
        response = {
            "status": 1,
            "data": {},
            "error": ""
        }
        existing_calendly_schedule = CalendlyCallSchedule.objects.filter(
            invitee_url=invitee_url)
        if existing_calendly_schedule:
            calendly_call_schedule_obj = existing_calendly_schedule[0]
            call_schedule_obj = CallSchedule.objects.get(pk=calendly_call_schedule_obj.call_schedule.pk)
            response["data"] = {
                "schedule_id": call_schedule_obj.pk,
                "reschedule_url": calendly_call_schedule_obj.reschedule_url,
                "cancel_url": calendly_call_schedule_obj.cancel_url,
                "status": call_schedule_obj.readable_status
            }
            return response

        event_details = self._get_event_details(invitee_url)

        if not event_details["status"]:
            response["status"] = 0
            response["error"] = event_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = self._create_call_schedule(
            visitor_user_obj, host_user_obj, event_details["data"])
        response["data"] = {
            "schedule_id": call_schedule_obj.pk,
            "reschedule_url": calendly_call_schedule_obj.reschedule_url,
            "cancel_url": calendly_call_schedule_obj.cancel_url,
            "status": call_schedule_obj.readable_status
        }
        return response

    def cancel_reschedule_scheduled_event(self, schedule_obj):
        response = {
            "status": 0,
            "message": "",
            "error": ""
        }
        calendly_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule=schedule_obj, is_active=True)
        event_details = self._get_event_details(calendly_schedule_obj.invitee_url)

        if not event_details["status"]:
            response["error"] = event_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = self._update_call_schedule(
            schedule_obj.id, event_details["data"])
        response["status"] = 1
        response["message"] = "Cancel/Reschedule event successful"

        return response

    def get_scheduled_event_details(self, call_schedule_objs):
        response = {
            "status": 0,
            "data": [],
            "error": ""
        }
        calendly_call_schedules = CalendlyCallSchedule.objects.filter(call_schedule__in=call_schedule_objs)

        if not calendly_call_schedules:
            response["error"] = "No calendly details for the schedule"
            return response

        response_data = []
        for calendly_schedule in calendly_call_schedules:
            schedule_detail = {
                "error": "",
                "schedule_id": calendly_schedule.call_schedule.id
            }
            customer_model_obj = calendly_schedule.call_schedule.visitor_user

            case_id = None
            try:
                case_id = customer_model_obj.users_cases.get(is_active=True).pk
            except ObjectDoesNotExist as err:
                err_msg = "No case for user - {} while getting schedule details " \
                          "with err - {}".format(customer_model_obj.pk, err)
                logger.info(logging_format(LOGGER_LOW_SEVERITY, "CalendlyScheduleManager:get_scheduled_event_details",
                                           customer_model_obj.pk, description=err_msg))

            event_details = self._get_event_details(calendly_schedule.invitee_url)
            if not event_details["status"]:
                schedule_detail["error"] = event_details["error"]
            else:
                details = event_details["data"]
                if not self._is_active_event(details):
                    continue
                schedule_detail.update({
                    "status": CallSchedule.STATUS_MAP.get(details["status"]),
                    "start_time": details["start_time_utc"],
                    "end_time": details["end_time_utc"],
                    "cancel_url": details["cancel_url"],
                    "reschedule_url": details["reschedule_url"],
                    "case_id": case_id,
                    "customer_profile_id": customer_model_obj.get_profile_id(),
                    "customer_name": customer_model_obj.get_profile_name()
                })
            response_data.append(schedule_detail)

        response["status"] = 1
        response["data"] = response_data
        return response

    def process_event_data(self, event_data):
        response = {
            "status": 0,
            "data": "",
            "error": ""
        }
        parser = CalendlyWebHookDataParser(event_data)

        if not parser.is_valid_data():
            response["error"] = parser.error
            return response
        extracted_details = parser.parse_extract_data()

        invitee_url_to_update = extracted_details["invitee_url_to_update"]
        try:
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.get(invitee_url=invitee_url_to_update).call_schedule
        except ObjectDoesNotExist:
            message = "CalendlyCallSchedule does not have any call schedule " \
                      "for invitee url - {}".format(invitee_url_to_update)
            logger.error(logging_format("", "CALENDLY-PROCESS_EVENT_DATA", "", description=message))
            response["error"] = message
            return response
        event_details = self._get_event_details(calendly_call_schedule_obj.invitee_url)

        if not event_details["status"]:
            response["error"] = event_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = self._update_call_schedule(
            calendly_call_schedule_obj.call_schedule.id, event_details["data"])
        response["status"] = 1
        response["message"] = "Web Hook data extraction successful"

        return response


def is_valid_webhook_signature(signature, body):
    if not (signature and body):
        return False
    try:
        string_body = json.dumps(body)
    except TypeError:
        error = "Error converting request.body to json string for body: {}".format(body)
        logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "WebHookProcessEvent.process_event", "", description=error))
        return False
    try:
        timstamp, v1 = signature.split(",")
        t_key, t_value = timstamp.split("=")
        v1_key, v1_value = v1.split("=")
    except ValueError as err:
        logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "IS_VALID_WEBHOOK_SIGNATURE",
                                    "", description=err))
        return False
    if t_key != CALENDLY_SIGNATURE_TKEY or v1_key != CALENDLY_SIGNATURE_VKEY:
        return False
    byte_key = settings.CALENDLY_SIGNING_KEY.encode('utf-8')
    message = t_value + "." + string_body

    expected_signature = hmac.new(byte_key, message.encode('utf-8'), hashlib.sha256).hexdigest()
    if expected_signature != v1_value:
        error = "Expected_signature - {} does not match signature {} for body - {}".format(expected_signature, v1_value, string_body)
        logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "IS_VALID_WEBHOOK_SIGNATURE",
                                    "", description=error))
        return False
    if int(t_value) * 1000 < int(datetime.datetime.utcnow().timestamp()) - CALENDLY_EVENT_TOLERANCE_TIME:
        error = "Event timestamp expired"
        logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "IS_VALID_WEBHOOK_SIGNATURE",
                                    "", description=error))
        return False

    return True


calendly_schedule_manager = CalendlyScheduleManager()
