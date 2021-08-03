from django.db.models import Count
from .models import Case

def get_rcic_cases_counts(agent):

	count_data = {
					"booked_count": 0,
					"in_progress_count": 0,
					"completed_count": 0,
					"cancelled_count": 0
				}

	try:
		count_list = Case.objects.filter(agent = agent, deleted_at__isnull = True).values("status").annotate(Count("case_id"))
	except Exception as e:
		log_error("ERROR", "get_rcic_cases_counts", str(agent.id), err = str(e))
		return count_data

	for each in count_list:
		if each['status'] == Case.BOOKED:
			count_data['booked_count'] = each['case_id__count']

		if each['status'] == Case.IN_PROGRESS:
			count_data['in_progress_count'] = each['case_id__count']

		if each['status'] == Case.COMPLETED:
			count_data['completed_count'] = each['case_id__count']

		if each['status'] == Case.CANCELLED:
			count_data['cancelled_count'] = each['case_id__count']

	return count_data