from keel.api.v1.auth.serializers import UserDetailsSerializer, UserDocumentSerializer
from keel.Core.err_log import log_error
from keel.tasks.models import Task, TaskComments, TaskTemplate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ListTaskSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=Task.STATUS_CHOICE, required=False)
    status_name = serializers.SerializerMethodField()
    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE, required=False)
    priority_name = serializers.SerializerMethodField()
    task_id = serializers.CharField(required=False)

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_priority_name(self, obj):
        return obj.get_priority_display()

    class Meta:
        model = Task
        fields = "__all__"


class TaskCommentSerializer(serializers.ModelSerializer):
    user_details = UserDetailsSerializer(source="user", many=False)

    class Meta:
        model = TaskComments
        fields = ("id", "user", "msg", "created_at", "user_details")


class TaskSerializer(ListTaskSerializer):
    tasks_comment = serializers.SerializerMethodField("get_task_comments")
    tasks_docs = serializers.SerializerMethodField("get_task_docs")

    def get_task_comments(self, task):
        qs = task.tasks_comment.filter(deleted_at__isnull=True).order_by("-id")
        serializer = TaskCommentSerializer(instance=qs, many=True)
        return serializer.data

    def get_task_docs(self, task):
        qs = task.tasks_docs.filter(deleted_at__isnull=True)
        serializer = UserDocumentSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Task
        fields = "__all__"


class CreateTaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComments
        fields = ("id", "user", "task", "msg")


class TaskCreateSerializer(serializers.ModelSerializer):

    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE)

    class Meta:
        model = Task
        fields = (
            "priority",
            "case",
            "user",
            "title",
            "description",
            "due_date",
            "task_id",
            "check_list",
            "tags",
            "is_template",
        )


class TaskUpdateSerializer(serializers.ModelSerializer):

    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICE)

    class Meta:
        model = Task
        fields = (
            "priority",
            "title",
            "description",
            "due_date",
            "task_id",
            "check_list",
            "tags",
            "is_template",
        )


class TaskStatusChangeSerializer(serializers.ModelSerializer):

    status = serializers.ChoiceField(choices=Task.STATUS_CHOICE)

    # TODO : Incase any validation to be done for status change, like Task is COMPLETED
    # def validate(self, attrs):
    #     if self.instance:
    #         if self.instance.status == self.instance.COMPLETED:
    #             raise ValidationError("Task Status is COMPLETED, cannot be changed")
    #     return attrs

    class Meta:
        model = Task
        fields = ("task_id", "status")


class TaskIDCheckSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=255)

    def validate(self, attrs):
        task_obj = ""
        task_id = attrs.get("task_id")

        if not task_id:
            raise serializers.ValidationError("Invalid Task Id")

        try:
            task_obj = Task.objects.prefetch_related("tasks_comment", "tasks_docs").get(
                task_id=task_id, deleted_at__isnull=True
            )
        except Task.DoesNotExist as e:
            log_error(
                "ERROR",
                "TaskIDCheckSerializer: validate",
                "",
                err=str(e),
                task_id=task_id,
            )
            raise serializers.ValidationError("Task Id does not exist")

        return task_obj


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = "__all__"
