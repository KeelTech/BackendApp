from keel.authentication.models import User
from keel.call_schedule.models import CallSchedule as CallScheduleModel
from keel.plans.implementation.plan_util_helper import PlanUtilHelper


class CallScheduleValidator(object):
    def __init__(self, customer_id):
        self._customer_id = customer_id
        self._customer_model_obj = None
        self._plan_id = None
        self._plan_util_helper = PlanUtilHelper()

    def call_schedule_allowed(self, plan_id):
        active_reschedule_call_exists = CallScheduleModel.objects.filter(
            visitor_user__id=self._customer_id, is_active=True,
            status__in=(CallScheduleModel.ACTIVE, CallScheduleModel.RESCHEDULED)).exists()

        if active_reschedule_call_exists:
            return False, "A call is already in progress"

        completed_call_count = CallScheduleModel.objects.select_for_update().filter(
            visitor_user__id=self._customer_id, is_active=True,
            status=CallScheduleModel.COMPLETED).count()

        if not plan_id:
            return (True, None) if completed_call_count == 0 else (False, "Only one call allowed when no plan is associated")

        self._plan_util_helper.plan_id = plan_id
        return self._plan_util_helper.can_schedule_more_calls(completed_call_count)


class CallScheduleHelper(object):
    def __init__(self, customer_id, call_schedule_client_type):
        self._customer_id = customer_id
        self._call_schedule_client_type = call_schedule_client_type

    def create_call_schedule(self, customer_model_obj, host_model_obj, start_time, end_time, status):
        return CallScheduleModel.objects.create(visitor_user=customer_model_obj, host_user=host_model_obj,
                                                call_schedule_client_type=self._call_schedule_client_type,
                                                start_time=start_time, end_time=end_time, status=status)
