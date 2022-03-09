from keel.notifications.constants import TASKS
from keel.notifications.models import InAppNotification

def create_task_notifcation(title, task_id, case):
    notification = InAppNotification.objects.create(
        text={"title": title, "task_id": task_id},
        case_id=case,
        category=TASKS,
    )
    return notification
