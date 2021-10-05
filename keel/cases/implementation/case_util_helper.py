from keel.cases.models import Case

class CaseUtilHelper(object):

    def __init__(self):
        self._case_id = None

    def get_case_details(self, case_model_obj):
        if not case_model_obj:
            return None
        return {
            "case_id": case_model_obj.case_id,
            "display_case_id": case_model_obj.display_id,
            "agent_id": case_model_obj.agent.pk,
            "account_manager_id": case_model_obj.account_manager_id,
        }

    def get_case_id_from_user_model_obj(self, user_model_objs):
        case_model_objs = Case.objects.filter(user__in=user_model_objs)
        customer_case_id_map = {}
        for case_obj in case_model_objs:
            customer_case_id_map[case_obj.user.pk] = case_obj.pk
        return customer_case_id_map
