from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import Http404
from keel.api.permissions import IsRCICUser
from keel.api.v1.auth.helpers import email_helper
from keel.api.v1.cases.serializers import CaseIDSerializer
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case
from keel.Core.constants import GENERIC_ERROR
from keel.Core.err_log import log_error
from keel.Core.helpers import generate_unique_id
from keel.notifications.constants import CHAT, DOCUMENT, HOME, TASKS
from keel.notifications.models import InAppNotification
from keel.tasks.models import Task, TaskComments, TaskTemplate
from rest_framework import mixins, serializers
from rest_framework import status as HTTP_STATUS
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .instances import create_template_task
from .serializers import (CreateTaskCommentSerializer, ListTaskSerializer,
                          TaskCreateSerializer, TaskIDCheckSerializer,
                          TaskSerializer, TaskStatusChangeSerializer,
                          TaskTemplateSerializer, TaskUpdateSerializer)

User = get_user_model()


class ListTask(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def count_tasks(self, validated_data):

        count_data = {"pending": 0, "in_review": 0, "completed": 0}

        try:
            validated_data.pop("status")
        except KeyError:
            pass

        count_list = Task.objects.filter(**validated_data, deleted_at__isnull=True)

        for each in count_list:
            if each.status == Task.PENDING:
                count_data["pending"] += 1

            if each.status == Task.IN_REVIEW:
                count_data["in_review"] += 1

            if each.status == Task.COMPLETED:
                count_data["completed"] += 1

        return count_data

    def list(self, request, format="json"):

        response = {
            "status": 0,
            "message": "Task list is successfully fetched",
            "data": [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        user = request.user
        user_id = user.id
        req_data = request.GET.dict()
        case_id = req_data.get("case", "")

        # validate Case ID against User/Agent
        case_serializer = CaseIDSerializer(
            data={"case_id": case_id, "user_id": user_id}
        )
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        # Validate Request Param Data
        try:
            req_data["user"] = case_obj.user_id
            task_validation = ListTaskSerializer(data=req_data)
            task_validation.is_valid(raise_exception=True)
            validated_data = task_validation.validated_data
        except ValidationError as e:
            log_error("ERORR", "ListTask: list validate_status", str(user), err=str(e))
            response["message"] = "Invalid Request Data {}".format(str(e))
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status=resp_status)

        # Filter the data as per req filters
        try:
            tasks = Task.objects.filter(
                **validated_data, deleted_at__isnull=True
            ).order_by("-updated_at")
            task_list_data = ListTaskSerializer(tasks, many=True)
            resp_data = task_list_data.data
            response["data"] = resp_data
        except Exception as e:
            log_error(
                "ERROR", "ListTask: list ListTaskSerializer", str(user), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        result = self.count_tasks(validated_data)
        response["task_count_per_status"] = result

        return Response(response, status=resp_status)

    def updateTask(self, request, format="json", **kwargs):

        response = {
            "status": 0,
            "message": "Task updated successfully",
            "data": [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        req_data = request.data
        user = request.user
        user_id = user.id
        req_data["user"] = user_id

        task_id = kwargs.get("task_id")

        task_serializer = TaskIDCheckSerializer(data={"task_id": task_id})
        task_serializer.is_valid(raise_exception=True)
        task_obj = task_serializer.validated_data

        req_data["task_id"] = task_id
        task_serializer = TaskUpdateSerializer(task_obj, data=req_data)
        task_serializer.is_valid(raise_exception=True)
        try:
            task_obj = task_serializer.save()
        except Exception as e:
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, resp_status)

        response["data"] = TaskSerializer(task_obj).data

        # send email to user after updating task
        context = {
            "name": task_obj.user.user_profile.first_name,
            "task_name": response["data"]["title"],
        }
        email_helper.send_update_task_email(context, user.email)

        return Response(response, status=HTTP_STATUS.HTTP_200_OK)


class TaskAdminOperations(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated, IsRCICUser)

    def createTask(self, request, format="json"):

        response = {
            "status": 0,
            "message": "Task created successfully",
            "data": [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        req_data = request.data
        user = request.user
        user_id = user.id

        case_id = req_data.get("case")

        case_serializer = CaseIDSerializer(
            data={"case_id": case_id, "user_id": user_id}
        )
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        # Task.User shud be a Case.Customer
        req_data["user"] = case_obj.user_id
        req_data["task_id"] = generate_unique_id("task_")

        task_serializer = TaskCreateSerializer(data=req_data)
        task_serializer.is_valid(raise_exception=True)
        try:
            task_obj = task_serializer.save()
        except Exception as e:
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, resp_status)

        response["data"] = TaskSerializer(task_obj).data

        # create an instance of Template task if is_template is True
        if task_obj.is_template:
            create_template_task(task_obj, user)

        # send email to user after creating task
        user = case_obj.user
        context = {
            "name": user.user_profile.first_name,
            "task_name": response["data"]["title"],
        }
        email_helper.send_create_task_email(context, user.email)

        return Response(response, status=HTTP_STATUS.HTTP_200_OK)

    def deleteTask(self, request, format="json", **kwargs):

        response = {"status": 0, "message": "Tasks deleted successfully", "data": ""}

        user = request.user
        user_id = user.id
        task_id = kwargs.get("task_id")

        try:
            task = Task.objects.prefetch_related("tasks_comment", "tasks_docs").get(
                task_id=task_id
            )
        except Task.DoesNotExist as e:
            log_error(
                "ERROR", "ListTask: deleteTask", str(user_id), err="Invalid Task Id"
            )
            response["message"] = "Task does not exist"
            response["status"] = 1
            return Response(response, status=HTTP_STATUS.HTTP_400_BAD_REQUEST)

        # Validate for Case, since only Assigned RCIC can delete the Task
        case_serializer = CaseIDSerializer(
            data={"case_id": task.case_id, "user_id": user_id}
        )
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        task.mark_delete()
        task.tasks_comment.update(
            deleted_at=datetime.now(pytz.timezone(settings.TIME_ZONE))
        )

        # send email to user after creating task
        user = task.user
        context = {"name": user.user_profile.first_name, "task_name": task.title}
        email_helper.send_delete_task_email(context, user.email)

        return Response(response, status=HTTP_STATUS.HTTP_200_OK)


class GetTaskDetails(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def taskDetails(self, request, format="json", **kwargs):

        response = {
            "status": 0,
            "message": "Task details are successfully fetched",
            "data": [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        user = request.user
        user_id = user.id
        task_id = kwargs.get("task_id")

        task_serializer = TaskIDCheckSerializer(data={"task_id": task_id})
        task_serializer.is_valid(raise_exception=True)
        task_obj = task_serializer.validated_data

        case_id = task_obj.case_id

        ## Validate User with Task.Case, so that only Case's Customer/RCIC shud be fetching task details
        case_serializer = CaseIDSerializer(
            data={"case_id": case_id, "user_id": user_id}
        )
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        resp_data = TaskSerializer(task_obj).data
        response["data"] = resp_data

        return Response(response, resp_status)


class CommentService(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def postComments(self, request, format="json"):

        response = {
            "status": 0,
            "message": "Comments posted",
            "data": {},
        }
        resp_status = HTTP_STATUS.HTTP_200_OK
        req_data = request.data

        user = request.user
        user_id = user.id
        req_data["user"] = user_id
        try:
            comment_serializer = CreateTaskCommentSerializer(data=req_data)
            comment_serializer.is_valid(raise_exception=True)
            # response['data'] = comment_serializer.validated_data
            comment_obj = comment_serializer.save()
            response["data"] = CreateTaskCommentSerializer(comment_obj).data

        except ValidationError as e:
            log_error(
                "ERORR", "CommentService: post postComments", str(user_id), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=resp_status)

    def deleteComments(self, request, format="json", **kwargs):

        response = {
            "status": 0,
            "message": "Comments deleted",
            "data": {},
        }

        user = request.user
        user_id = user.id

        resp_status = HTTP_STATUS.HTTP_200_OK
        comment_id = kwargs.get("comment_id")

        try:
            comment_obj = TaskComments.objects.get(id=comment_id, user=user_id)
        except TaskComments.DoesNotExist as e:
            log_error(
                "ERROR",
                "CommentService: delete delete_comments",
                str(user_id),
                err=str(e),
            )
            response["message"] = "Comment Id does not exist"
            response["status"] = 1
            return Response(response, status=HTTP_STATUS.HTTP_400_BAD_REQUEST)

        comment_obj.mark_delete()
        return Response(response, status=resp_status)


class TaskStatusChange(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def StatusEdit(self, request, format="json", **kwargs):

        response = {
            "status": 0,
            "message": "Task Status Updated successfully",
            "data": {},
        }

        user = request.user
        user_id = user.id
        req_data = request.data

        task_id = kwargs.get("task_id")

        if not task_id:
            log_error(
                "ERROR",
                "TaskStatusChange: StatusEdit",
                str(user_id),
                err_msg="Invalid Task Id",
            )
            response["message"] = "Task does not exist"
            response["status"] = 1
            return Response(response, status=HTTP_STATUS.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(task_id=task_id, deleted_at__isnull=True)
        except Task.DoesNotExist as e:
            log_error("ERROR", "TaskStatusChange: StatusEdit", str(user_id), err=str(e))
            response["message"] = "Task does not exist"
            response["status"] = 1
            return Response(response, status=HTTP_STATUS.HTTP_400_BAD_REQUEST)

        req_data["task_id"] = task_id
        try:

            status_serilizer = TaskStatusChangeSerializer(task, data=req_data)
            status_serilizer.is_valid(raise_exception=True)
            task_obj = status_serilizer.save()
            response["data"] = TaskSerializer(task_obj).data

        except ValidationError as e:
            log_error(
                "ERROR", "TaskStatusChange : StatusEdit", str(user_id), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            return Response(response, status=HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status=HTTP_STATUS.HTTP_200_OK)


class GetTemplateTask(GenericViewSet):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsRCICUser)
    authentication_classes = (JWTAuthentication,)

    def get_templated_task(self, request):
        response = {
            "status": 0,
            "message": "Task list is successfully fetched",
            "data": [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        user = request.user
        user_id = user.id
        req_data = request.GET.dict()

        # Filter the data as is_template = False
        try:
            tasks = Task.objects.filter(case__agent=user, is_template=True)
            task_list_data = ListTaskSerializer(tasks, many=True)
            resp_data = task_list_data.data
            response["data"] = resp_data
        except Exception as e:
            log_error(
                "ERROR", "ListTask: list ListTaskSerializer", str(user_id), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status=resp_status)


class TaskTemplateView(GenericViewSet):
    serializer_class = TaskTemplateSerializer
    permission_classes = (IsAuthenticated, IsRCICUser)
    authentication_classes = (JWTAuthentication,)

    def get_object(self, pk):
        try:
            return TaskTemplate.objects.get(pk=pk)
        except TaskTemplate.DoesNotExist:
            raise Http404

    def update(self, request, pk):
        response = {
            "status": 1,
            "message": "Task Template Updated Successfully",
            "data": {},
        }
        queryset = self.get_object(pk)
        serializer = TaskTemplateSerializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()

        except Exception as e:
            log_error(
                "ERROR", "TaskTemplateView: update", str(request.user), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 0
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        response["data"] = serializer.data
        return Response(response)

    def list_task_template(self, request):
        response = {
            "status": 0,
            "message": "Task Template list is successfully fetched",
            "data": [],
        }
        queryset = request.user.agent_task_template.all()
        serializer = TaskTemplateSerializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response)

    def delete(self, request, pk):
        response = {
            "status": 0,
            "message": "Task Template Deleted Successfully",
            "data": {},
        }
        queryset = self.get_object(pk)
        try:
            queryset.delete()
        except Exception as e:
            log_error(
                "ERROR", "TaskTemplateView: delete", str(request.user), err=str(e)
            )
            response["message"] = GENERIC_ERROR
            response["status"] = 0
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response)
