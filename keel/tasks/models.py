from django.db import models
from keel.authentication.models import User
from keel.cases.models import Case
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from .utils import create_task_notifcation

# Create your models here.


class Task(TimeStampedModel, SoftDeleteModel):

    LOW = 0
    HIGH = 1
    MEDIUM = 2
    PRIORITY_CHOICE = ((LOW, "Low"), (HIGH, "High"), (MEDIUM, "Medium"))

    PENDING = 0
    IN_REVIEW = 1
    COMPLETED = 2
    STATUS_CHOICE = (
        (PENDING, "Pending"),
        (IN_REVIEW, "In Review"),
        (COMPLETED, "Completed"),
    )

    task_id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    case = models.ForeignKey(
        Case,
        on_delete=models.deletion.DO_NOTHING,
        null=True,
        blank=True,
        related_name="cases_tasks",
    )
    priority = models.SmallIntegerField(default=MEDIUM, choices=PRIORITY_CHOICE)
    tags = models.CharField(null=True, max_length=255)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=PENDING, choices=STATUS_CHOICE)
    check_list = models.JSONField(default=dict, null=True)
    user = models.ForeignKey(
        User, on_delete=models.deletion.DO_NOTHING, related_name="user_tasks"
    )
    is_template = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.task_id and (
            self.status == self.PENDING or self.status == self.COMPLETED
        ):
            create_task_notifcation(self.title, self.task_id, self.case)
        
        super().save(*args, **kwargs)


class TaskComments(TimeStampedModel, SoftDeleteModel):

    user = models.ForeignKey(
        User, on_delete=models.deletion.DO_NOTHING, related_name="users_comment"
    )
    task = models.ForeignKey(
        Task, on_delete=models.deletion.DO_NOTHING, related_name="tasks_comment"
    )
    msg = models.TextField(null=True, blank=True)


class TaskTemplate(TimeStampedModel, SoftDeleteModel):
    agent = models.ForeignKey(
        User,
        on_delete=models.deletion.DO_NOTHING,
        related_name="agent_task_template",
        default=None,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=512, default=None, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    checklist = models.JSONField(default=dict, null=True, blank=True)
    priority = models.CharField(max_length=512, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
