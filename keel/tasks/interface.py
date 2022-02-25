from django.db.models import Count, Q
from .models import Task


def get_rcic_task_counts(agent):

    count_value = 0
    try:
        count_value = Task.objects.filter(
            ~Q(status=Task.COMPLETED), case__agent=agent, deleted_at__isnull=True
        ).count()
    except Exception as e:
        log_error("ERROR", "get_rcic_task_counts", str(agent.id), err=str(e))

    return count_value