from keel.plans.models import Plan


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
    return Plan.objects.filter(id=plan_id).first() if not None else None
