from django.contrib import admin
from .models import Task, TaskComments

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskComments)
