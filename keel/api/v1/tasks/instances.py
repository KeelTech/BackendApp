from keel.tasks.models import TaskTemplate

def create_template_task(task_obj, user):
    """
    Creates a new template from a task object.
    """
    template = TaskTemplate(
        agent = user,
        title = task_obj.title,
        description = task_obj.description,
        checklist = task_obj.check_list,
        priority = task_obj.priority,
        created_at = task_obj.created_at,
        updated_at = task_obj.updated_at,
    )
    template.save()
    return template