from keel.notifications.constants import TASKS
from keel.notifications.models import InAppNotification

def create_task_notifcation(title, task_id, user, case):
    notification = InAppNotification.objects.create(
        text={"title": title, "task_id": task_id},
        user_id=user,
        case_id=case,
        category=TASKS,
    )
    return notification
