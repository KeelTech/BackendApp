from keel.Core.admin import CustomBaseModelAdmin
from django.contrib import admin
from .models import Task, TaskComments, TaskTemplate

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'case', 'status', 'user')
    autocomplete_fields = ['case', 'user']
    readonly_fields = ('deleted_at', )

class TaskCommentsAdmin(CustomBaseModelAdmin):
    pass

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskComments, TaskCommentsAdmin)
admin.site.register(TaskTemplate)
