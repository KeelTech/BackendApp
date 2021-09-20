from keel.authentication.models import User
from keel.call_schedule.models import CallSchedule as CallScheduleModel
from keel.plans.implementation.plan_util_helper import PlanUtilHelper


class ICallScheduleValidator(object):

    def call_schedule_allowed(self, plan_id):
        raise NotImplementedError


class CallScheduleValidator(ICallScheduleValidator):
    def __init__(self, customer_id):
        self._customer_id = customer_id
        self._customer_model_obj = None
        self._plan_id = None
        self._plan_util_helper = PlanUtilHelper()

    def call_schedule_allowed(self, plan_id):
        active_completed_call_count = CallScheduleModel.objects.select_for_update().filter(
            visitor_user__id=self._customer_id, is_active=True,
            status__in=(CallScheduleModel.ACTIVE, CallScheduleModel.RESCHEDULED)).count()

        if not plan_id:
            return True if active_completed_call_count == 0 else False

        self._plan_util_helper.plan_id = plan_id
        return self._plan_util_helper.can_schedule_more_calls(active_completed_call_count)
