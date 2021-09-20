
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
