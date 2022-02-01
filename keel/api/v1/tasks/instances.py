from keel.tasks.models import TaskTemplate


def create_template_task(task_obj, user):
    """
    Creates a new template from a task object.
    """
    template = TaskTemplate(
        agent=user,
        title=task_obj.title,
        description=task_obj.description,
        checklist=task_obj.check_list,
        priority=task_obj.priority,
        created_at=task_obj.created_at,
        updated_at=task_obj.updated_at,
    )
    template.save()
    return template


def number_of_tasks_per_status(obj):
    
    # get number of tasks related to cases from Task Model
    tasks = 0
    pending_tasks = 0
    in_review_tasks = 0
    completed_tasks = 0

    for task in obj.cases_tasks.all():
        tasks += 1
        if task.status == 0:
            pending_tasks += 1
        elif task.status == 1:
            in_review_tasks += 1
        elif task.status == 2:
            completed_tasks += 1

    return {
        "tasks": tasks,
        "pending_tasks": pending_tasks,
        "in_review_tasks": in_review_tasks,
        "completed_tasks": completed_tasks,
    }
