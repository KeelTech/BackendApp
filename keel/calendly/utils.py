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
    def __init__(self):
        self._scheduled_event_details = None

    def _update_call_schedule(self, call_schedule_id, event_invitee_details):
        call_schedule_status = event_invitee_details["status"] if not event_invitee_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "start_time": event_invitee_details["start_time"],
            "end_time": event_invitee_details["end_time"],
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

    def _create_call_schedule(self, call_schedule_model_obj, event_details):
        calendly_call_schedule_details = dict({
            "invitee_url": event_details["invitee_url"],
            "cancel_url": event_details["cancel_url"],
            "reschedule_url": event_details["reschedule_url"],
            "communication_means": event_details["location"],
            "status": event_details["status"]
        })
        calendly_call_schedule_details["call_schedule"] = call_schedule_model_obj
        calendly_call_schedule_obj = CalendlyCallSchedule.objects.create(**calendly_call_schedule_details)
        return calendly_call_schedule_obj

    def _is_active_event(self, event_details):
        if parser.parse(event_details["end_time"]) <= timezone.now():
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
        if not calendly_user_obj.event_type_url:
            message = "Event resource url not present for the "\
                      "calendly user: {}".format(host_user_obj.email)
            logger.error(logging_format("", "CALENDLY-GET_AGENT_SCHEDULE_URL", "", description=message))
            return scheduling_url

        schedule_url_details = CalendlyApis.single_use_scheduling_link(
            calendly_user_obj.event_type_url, 1, invitee_obj.get_profile_name(), invitee_obj.email)

        if not schedule_url_details["status"]:
            return scheduling_url
        return schedule_url_details["schedule_url"]

    def schedule_identifier_exists(self, invitee_url):
        return CalendlyCallSchedule.objects.filter(invitee_url=invitee_url).exists()

    def get_schedule_identifier_details(self, invitee_url):
        if self._scheduled_event_details:
            return self._scheduled_event_details
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        resp_invitee_details = CalendlyApis.get_invitee_details(invitee_url)
        if not resp_invitee_details["status"]:
            response["error"] = "Error in getting Invitee details"
            return response
        resp_event_details = CalendlyApis.get_event_details(
            resp_invitee_details["data"]["event_resource_url"])

        if not resp_event_details["status"]:
            response["error"] = "Error in getting Event details"
            return response

        event_data = resp_event_details["data"]
        event_data.update(resp_invitee_details["data"])
        event_data["status"] = event_data["status"] if not event_data[
            "rescheduled"] else CallSchedule.RESCHEDULED
        response["data"] = {
            "status": event_data["status"],
            "start_time": event_data["start_time_utc"],
            "end_time": event_data["end_time_utc"],
            "invitee_url": event_data["invitee_url"],
            "cancel_url": event_data["cancel_url"],
            "reschedule_url": event_data["reschedule_url"],
            "location": event_data["location"],
        }
        response["status"] = 1
        self._scheduled_event_details = response
        return response

    def create_event_schedule(self, call_schedule_model_obj, invitee_url):
        event_details = self.get_schedule_identifier_details(invitee_url)
        if not (event_details and event_details["status"]):
            raise ValueError("Error getting event details")
        calendly_call_schedule_obj = self._create_call_schedule(
            call_schedule_model_obj, event_details["data"])
        return {
            "reschedule_url": calendly_call_schedule_obj.reschedule_url,
            "cancel_url": calendly_call_schedule_obj.cancel_url
        }

    def cancel_reschedule_scheduled_event(self, schedule_obj):
        response = {
            "status": 0,
            "message": "",
            "error": ""
        }
        calendly_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule=schedule_obj, is_active=True)
        event_details = self.get_schedule_identifier_details(calendly_schedule_obj.invitee_url)

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

            event_details = self.get_schedule_identifier_details(calendly_schedule.invitee_url)
            if not event_details["status"]:
                schedule_detail["error"] = event_details["error"]
            else:
                details = event_details["data"]
                if not self._is_active_event(details):
                    continue
                schedule_detail.update({
                    "status": CallSchedule.STATUS_MAP.get(details["status"]),
                    "start_time": details["start_time"],
                    "end_time": details["end_time"],
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
        event_details = self.get_schedule_identifier_details(calendly_call_schedule_obj.invitee_url)

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
