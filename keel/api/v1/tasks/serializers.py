from rest_framework import serializers
from keel.tasks.models import Task, TaskComments

class ListTaskSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    task_id = serializers.CharField(required=False)

    def get_status(self, obj):
        return obj.get_status_display()

    def get_priority(self, obj):
        return obj.get_priority_display()

    def validate_status(self, value):
        if value not in dict(Task.STATUS_CHOICE):
            raise serializers.ValidationError("Status Choice is Invalid")   
        return value

    class Meta:
        model = Task
        fields = ('task_id','status','priority','created_at','title')


class TaskSerializer(ListTaskSerializer):

    class Meta:
        model = Task
        fields = ('task_id','status','priority','created_at','title','description','due_date')


