from keel.plans.models import Plan
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error


class PlanUtilHelper:
    def __init__(self):
        self._customer_id = None
        self._plan_id = None

    @property
    def plan_id(self):
        return self._plan_id

    @plan_id.setter
    def plan_id(self, value):
        self._plan_id = value

    def can_schedule_more_calls(self, active_completed_call_count):
        if not self._plan_id:
            raise ValueError("Plan Id not populated")
        # TODO: Implement Logic related to scheduled call and Plan
        return True, None

    def get_plan_details(self, plan_model_obj):
        return {
            "title": plan_model_obj.title,
            "description": plan_model_obj.description,
            "total_plan_price": plan_model_obj.price,
            "currency": plan_model_obj.currency,
        }


def get_plan_instance_with_id(plan_id):
    response = {"message": "", "plan_obj": "", "status": 1}
    try:
        plan_model_obj = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist as err:
        log_error(
            LOGGER_LOW_SEVERITY,
            "plan_util_helper:get_plan_instance_with_id",
            "",
            description=str(err),
        )
        response["status"] = 0
        response["message"] = f"Plan with id {plan_id} does not exist"
        return response
    response["plan_obj"] = plan_model_obj
    return response
