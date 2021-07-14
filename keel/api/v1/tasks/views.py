
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status as HTTP_STATUS
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error
from keel.Core.constants import GENERIC_ERROR
from keel.tasks.models import Task, TaskComments

from .serializers import ListTaskSerializer, TaskSerializer, CreateTaskCommentSerializer


class ListTask(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def list(self, request, format = 'json'):
        response = {
            "status" : 0,
            "message" : "Task list is successfully fetched",
            "data" : [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        user = request.user
        user_id = user.id
        req_data = request.GET
        status = req_data.get("status","")

        if status is None or ( type(status) is str and not status.isnumeric()):
            log_error("ERROR","ListTask: list", str(user_id), err = "invalid status data", msg = str(status))
            response["message"] = "Invalid Status Choice"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        status = int(status)
        try:
            task_validation = ListTaskSerializer(data = {"status":status})
            task_validation.is_valid(raise_exception = True) 
        except ValidationError as e:
            log_error("ERORR","ListTask: list validate_status", str(user_id), err = str(e), data = str(status))
            response["message"] = "Invalid Status Choice value"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        try:
            tasks = Task.objects.filter(status = status, user_id = user_id)
            task_list_data = ListTaskSerializer(tasks, many = True)
            resp_data = task_list_data.data    
            response['data'] = resp_data 
        except Exception as e:
            log_error("ERROR","ListTask: list ListTaskSerializer", str(user_id), err = str(e))
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status = resp_status)

class GetTaskDetails(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def taskDetails(self, request, format = 'json', **kwargs):

        response = {
            "status" : 0,
            "message" : "Task details are successfully fetched",
            "data" : [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        user = request.user
        user_id = user.id
        task_id = kwargs.get("task_id")
        try:
            task = Task.objects.prefetch_related("tasks_comment","tasks_docs").get(task_id = task_id, user_id = user_id)
            # task = Task.objects.get(task_id = task_id, user_id = user_id)
            task_data = TaskSerializer(task)
            resp_data = task_data.data
            response['data'] = resp_data

        except Task.DoesNotExist:
            log_error("ERROR","GetTaskDetails:fetch", str(user_id), err = "Task DoesNotExist", task_id = task_id)
            response['status'] = 1
            response['message'] = 'Task Id is invalid'
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST

        except Exception as e:
            log_error("ERROR","GetTaskDetails:fetch", str(user_id), err = str(e), msg = "Unknown exception")
            response['status'] = 1
            response['message'] = GENERIC_ERROR
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, resp_status)


class CommentService(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    
    def postComments(self, request, format = 'json'):

        response = {
            "status" : 0,
            "message" : "Comments posted",
            "data" : {},        
        }    
        resp_status = HTTP_STATUS.HTTP_200_OK
        req_data = request.POST.dict() 

        user = request.user
        user_id = user.id
        req_data['user'] = user_id
        try:

            comment_serializer = CreateTaskCommentSerializer(data = req_data)
            comment_serializer.is_valid(raise_exception = True)
            # response['data'] = comment_serializer.validated_data
            comment_obj = comment_serializer.save()
            response['data'] = CreateTaskCommentSerializer(comment_obj).data

        except ValidationError as e:
            log_error("ERORR","CommentService: post postComments", str(user_id), err = str(e))
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status = resp_status)

    def deleteComments(self, request, format = 'json', **kwargs):

        response = {
            "status" : 0,
            "message" : "Comments deleted",
            "data" : {},            
        }

        user = request.user
        user_id = user.id

        resp_status = HTTP_STATUS.HTTP_200_OK
        comment_id = kwargs.get("comment_id")

        try:
            comment_obj = TaskComments.objects.get(id = comment_id, user = user_id)
        except TaskComments.DoesNotExist as e:
            log_error("ERROR", "CommentService: delete delete_comments",str(user_id), err = str(e))
            response["message"] = "Comment Id does not exist"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        comment_obj.mark_delete()

        return Response(response, status = resp_status)





