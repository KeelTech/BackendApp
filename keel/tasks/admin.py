from django.contrib import admin
from .models import Task, TaskComments

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'case', 'status', 'user')
    autocomplete_fields = ['case', 'user']
    readonly_fields = ('deleted_at', )

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskComments)
