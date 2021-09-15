
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
        return True
