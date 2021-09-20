from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from keel.call_schedule.models import CallSchedule
from keel.calendly.utils import CalendlyScheduleManager
from keel.authentication.models import User
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_MODERATE_SEVERITY

from .call_schedule import CallScheduleValidator

import logging
logger = logging.getLogger('app-logger')


class CallScheduleManager(object):

    def __init__(self, user_id, call_schedule_client_type):
        self._user_id = user_id
        self._user_model_obj = None
        self._user_case_model_obj = None
        self._client_scheduler = schedule_client_factory.get_scheduler_client(call_schedule_client_type)
        self._call_schedule_validator = CallScheduleValidator(user_id)

    def _get_host_user_obj(self):
        return self._user_case_model_obj.agent if self._user_case_model_obj else User.objects.get(
            user_type=User.ACCOUNT_MANAGER, call_default_contact=True)

    def _get_host_plan(self):
        if not self._user_case_model_obj:
            return None
        return self._user_case_model_obj.plan.pk

    def _get_case_model_obj(self):
        try:
            case_model_obj = self._user_model_obj.users_cases.get(is_active=True)
        except (ObjectDoesNotExist, MultipleObjectsReturned) as err:
            return None
        return case_model_obj

    def _get_user_model_obj(self):
        return User.objects.get(pk=self._user_id, is_active=True)

    def generate_schedule_url(self):
        self._user_model_obj = self._get_user_model_obj()
        self._user_case_model_obj = self._get_case_model_obj()
        plan_id = self._get_host_plan()
        if not self._call_schedule_validator.call_schedule_allowed(plan_id):
            err_msg = "User - {} cannot schedule further calls".format(self._user_id)
            logger.error(logging_format(LOGGER_MODERATE_SEVERITY, "CallScheduleManager:generate_schedule_url",
                                        self._user_id, description=err_msg))
            return None
        host_user_obj = self._get_host_user_obj()
        return self._client_scheduler.get_schedule_url(self._user_model_obj, host_user_obj)

    def create_schedule(self, client_invitee_identifier):
        self._user_model_obj = User.objects.get(pk=self._user_id, is_active=True)
        self._user_case_model_obj = self._get_case_model_obj()
        host_user_obj = self._get_host_user_obj()
        return self._client_scheduler.create_event_schedule(self._user_model_obj, host_user_obj, client_invitee_identifier)

    def get_schedules(self):
        response = {
            "status": 0,
            "data": [],
            "error": ""
        }
        user = User.objects.get(pk=self._user_id, is_active=True)
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

    def webhook_process_event(self):
        pass

    def webhook_subscribe(self):
        pass


class ScheduleClientFactory:
    _call_scheduler_client_map = {
        CallSchedule.CALENDLY_CALL_SCHEDULE_CLIENT: CalendlyScheduleManager()
    }

    _default_scheduler_client = CalendlyScheduleManager()

    def get_scheduler_client(self, client_type):
        return self._call_scheduler_client_map.get(client_type, self._default_scheduler_client)


schedule_client_factory = ScheduleClientFactory()
