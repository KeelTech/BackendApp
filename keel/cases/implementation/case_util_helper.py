from keel.cases.models import Case
from keel.plans.models import Plan

class CaseUtilHelper(object):

    def __init__(self):
        self._case_id = None

    def get_case_details(self, case_model_obj):
        if not case_model_obj:
            return None
        return {
            "case_id": case_model_obj.case_id,
            "display_case_id": case_model_obj.display_id,
            "agent_id": case_model_obj.agent.pk if case_model_obj.agent else None,
            "account_manager_id": case_model_obj.account_manager.pk if case_model_obj.account_manager else None,
        }

    def get_case_id_from_user_model_obj(self, user_model_objs):
        case_model_objs = Case.objects.filter(user__in=user_model_objs, is_active=True)
        customer_case_id_map = {}
        for case_obj in case_model_objs:
            customer_case_id_map[case_obj.user.pk] = case_obj.pk
        return customer_case_id_map

    def create_with_free_plan(self, customer_model_obj, currency, plan_model_obj=None):
        if not plan_model_obj:
            plan_model_obj = Plan.objects.get(type=Plan.FREE_PLAN_TYPE, currency=currency)
        return Case.objects.create(user=customer_model_obj, plan=plan_model_obj)
