from django.contrib import admin
from .models import Case, Task, TaskComments

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskComments)
admin.site.register(Case)
