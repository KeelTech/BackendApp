from django.db import models
from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User

# Create your models here.

class Case(TimeStampedModel, SoftDeleteModel):

    case_id = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_cases')
    agent = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='agents_cases')
    account_manager_id = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(verbose_name= 'Active', default=True)
    ref_id = models.ForeignKey('self',null=True, blank=True, on_delete=models.deletion.DO_NOTHING)
    # plan_id = models.IntegerField(null=True, blank=True) TODO


class Task(TimeStampedModel, SoftDeleteModel):

    LOW = 0
    HIGH = 1
    MEDIUM = 2
    PRIORITY_CHOICE = ((LOW, 'Low'),
                     (HIGH, 'High'),
                     (MEDIUM,'Medium'))

    PENDING = 0
    IN_PROGESS = 1
    COMPLETED = 2
    STATUS_CHOICE = ((PENDING,'Pending'),
                    (IN_PROGESS,'In Progress'),
                    (COMPLETED, 'Completed'))

    task_id = models.CharField(max_length=255, primary_key=True)
    title = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    case = models.ForeignKey(Case, on_delete=models.deletion.DO_NOTHING, null=True, blank=True, related_name='cases_tasks')
    priority = models.SmallIntegerField(default=MEDIUM,
                                          choices=PRIORITY_CHOICE)
    tags = models.SmallIntegerField(null=True) # TODO: to be changed later
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=PENDING,
                                          choices=STATUS_CHOICE)
    check_list = models.JSONField(default =dict, null=True) 
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name = "user_tasks")

class TaskComments(TimeStampedModel, SoftDeleteModel):

    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='users_comment')
    task = models.ForeignKey(Task, on_delete=models.deletion.DO_NOTHING, related_name='tasks_comment')
    msg = models.TextField(null=True,blank=True)

