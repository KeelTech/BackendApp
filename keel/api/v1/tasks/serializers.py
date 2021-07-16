from rest_framework import serializers

from keel.api.v1.auth.serializers import UserDetailsSerializer, UserDocumentSerializer
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
    user_details = UserDetailsSerializer(source = 'user',many = False)

    class Meta:
        model = TaskComments
        fields = ('id','user','msg','created_at','user_details')

class TaskSerializer(ListTaskSerializer):
    tasks_comment = serializers.SerializerMethodField("get_task_comments")
    tasks_docs = UserDocumentSerializer(many = True)

    def get_task_comments(self, task):
        qs = task.tasks_comment.filter(deleted_at__isnull = True)
        serializer = TaskCommentSerializer(instance=qs, many=True)
        return serializer.data        

    class Meta:
        model = Task
        fields = ('task_id','status_name','priority_name','created_at',
                    'title','description','due_date','tasks_comment', 'tasks_docs',
                    'check_list','tags','case_id')

class CreateTaskCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskComments
        fields = ('id','user','task','msg')


class TaskCreateSerializer(serializers.ModelSerializer):

    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE)

    class Meta:
        model = Task
        fields = ('priority','case','user','title','description','due_date','task_id','check_list','tags')


class TaskUpdateSerializer(serializers.ModelSerializer):

    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE)

    class Meta:
        model = Task
        fields = ('priority','title','description','due_date','task_id','check_list','tags')




