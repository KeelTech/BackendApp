from keel.tasks.models import TaskTemplate

def create_template_task(task_obj):
    """
    Creates a new template from a task object.
    """
    template = TaskTemplate(
        title = task_obj.title,
        description = task_obj.description,
        checklist = task_obj.check_list,
        created_at = task_obj.created_at,
        updated_at = task_obj.updated_at,
    )
    template.save()
    return template