from keel.cases.interface import get_rcic_cases_counts
from keel.tasks.interface import get_rcic_task_counts


def get_rcic_item_counts(user):

    resp = {}; err_msg = ''

    resp['cases_count'] = get_rcic_cases_counts(user)
    resp['task_count'] = get_rcic_task_counts(user)

    # TODO: Change below
    resp['meeting_count'] = 0
    resp['earnings_count'] = 0

    return resp, err_msg
