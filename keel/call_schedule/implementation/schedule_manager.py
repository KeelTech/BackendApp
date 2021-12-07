from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction

from keel.call_schedule.models import CallSchedule
from keel.calendly.utils import CalendlyScheduleManager
from keel.authentication.models import User
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_MODERATE_SEVERITY

from .call_schedule import CallScheduleValidator, CallScheduleHelper

import logging
logger = logging.getLogger('app-logger')


class CallScheduleManager(object):

    def __init__(self, customer_id, call_schedule_client_type):
        self._customer_id = customer_id
        self._customer_model_obj = None
        self._customer_case_model_obj = None
        self._client_scheduler, self._call_schedule_client_type = schedule_client_factory.get_scheduler_client(call_schedule_client_type)
        self._call_schedule_validator = CallScheduleValidator(customer_id)
        self._call_schedule_helper = CallScheduleHelper(customer_id, call_schedule_client_type)

    def _get_host_user_obj(self):
        return self._customer_case_model_obj.agent if self._customer_case_model_obj else User.objects.get(
            user_type=User.ACCOUNT_MANAGER, call_default_contact=True)

    def _get_customer_plan(self):
        if not self._customer_case_model_obj:
            return None
        return self._customer_case_model_obj.plan.pk

    def _get_case_model_obj(self):
        try:
            case_model_obj = self._customer_model_obj.users_cases.get(is_active=True)
        except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
            return None
        return case_model_obj

    def _get_customer_model_obj(self):
        return User.objects.get(pk=self._customer_id, is_active=True)

    def generate_schedule_url(self):
        response = {
            "status": 1,
            "schedule_url": None,
            "error": None
        }
        self._customer_model_obj = self._get_customer_model_obj()
        self._customer_case_model_obj = self._get_case_model_obj()
        plan_id = self._get_customer_plan()
        can_customer_schedule_call, cannot_schedule_call_reason = self._call_schedule_validator.call_schedule_allowed(plan_id)
        if not can_customer_schedule_call:
            err_msg = "User - {} cannot schedule further calls".format(self._customer_id)
            logger.error(logging_format(LOGGER_MODERATE_SEVERITY, "CallScheduleManager:generate_schedule_url",
                                        self._customer_id, description=err_msg))
            response["status"] = 0
            response["error"] = cannot_schedule_call_reason
            return response
        host_user_obj = self._get_host_user_obj()
        response["schedule_url"] = self._client_scheduler.get_schedule_url(self._customer_model_obj, host_user_obj)
        return response

    def create_schedule(self, client_schedule_identifier):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        self._customer_model_obj = User.objects.get(pk=self._customer_id, is_active=True)
        self._customer_case_model_obj = self._get_case_model_obj()
        host_user_obj = self._get_host_user_obj()
        if self._client_scheduler.schedule_identifier_exists(client_schedule_identifier):
            response["error"] = "Client schedule identifier already exists"
            return response
        client_schedule_details = self._client_scheduler.get_schedule_identifier_details(client_schedule_identifier)
        if not client_schedule_details["status"]:
            response["error"] = client_schedule_details["error"]
            return response
        try:
            with transaction.atomic():
                details = client_schedule_details["data"]
                call_schedule_model_obj = self._call_schedule_helper.create_call_schedule(
                    self._customer_model_obj, host_user_obj, details["start_time"], details["end_time"], details["status"])
                client_resp_details = self._client_scheduler.create_event_schedule(call_schedule_model_obj, invitee_url=client_schedule_identifier)
                response["data"].update(client_resp_details)
                response["data"].update({
                    "status": call_schedule_model_obj.readable_status,
                    "schedule_id": call_schedule_model_obj.pk
                })
                response["status"] = 1
        except ValueError as err:
            response["error"] = "Error while creating call schedule and client call schedule"
            return response
        return response

    def get_schedules(self):
        response = {
            "status": 0,
            "data": [],
            "error": ""
        }
        user = User.objects.get(pk=self._customer_id, is_active=True)
        query = {
            "is_active": True,
            "status__in": (CallSchedule.ACTIVE, CallSchedule.RESCHEDULED)
        }
        if user.user_type == User.CUSTOMER:
            query.update({"visitor_user": user})
        else:
            query.update({"host_user": user})
        call_schedule_objs = CallSchedule.objects.filter(**query)
        if not call_schedule_objs.exists():
            response["status"] = 1
            return response
        return self._client_scheduler.get_scheduled_event_details(call_schedule_objs=call_schedule_objs)

    def update_call_schedule(self, schedule_id, schedule_details):
        return CallSchedule.objects.select_for_update().get(id=schedule_id).update(**schedule_details)

    def webhook_process_event(self, schedule_data):
        response = {
            "status": 0,
            "data": "",
            "error": ""
        }
        validated_details = self._client_scheduler.validate_parse_schedule_event_data(schedule_data)
        if not validated_details["status"]:
            response["error"] = validated_details["error"]
            return response
        process_response = self._client_scheduler.process_event_data(self, validated_details)
        return process_response

    def webhook_subscribe(self):
        pass


class ScheduleClientFactory:
    _call_scheduler_client_map = {
        CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT: CalendlyScheduleManager()
    }

    _default_scheduler_client = CalendlyScheduleManager()
    _default_scheduler_client_type = CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT

    def get_scheduler_client(self, client_type):
        scheduler_client = self._call_scheduler_client_map.get(client_type)

        if scheduler_client:
            return scheduler_client, client_type
        else:
            return self._default_scheduler_client, self._default_scheduler_client_type


schedule_client_factory = ScheduleClientFactory()
