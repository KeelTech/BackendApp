from rest_framework import serializers
from keel.tasks.models import Task, TaskComments

class ListTaskSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=Task.STATUS_CHOICE)
    status_name = serializers.SerializerMethodField()
    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE, required = False)
    priority_name = serializers.SerializerMethodField()
    task_id = serializers.CharField(required=False)

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_priority_name(self, obj):
        return obj.get_priority_display()

    class Meta:
        model = Task
        fields = ('task_id','status_name','priority_name','priority','status','created_at','title')


class TaskCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskComments
        fields = ('user','msg')

class TaskSerializer(ListTaskSerializer):
    tasks_comment = TaskCommentSerializer(many= True)

    class Meta:
        model = Task
        fields = ('task_id','status_name','priority_name','created_at','title','description','due_date','tasks_comment')


