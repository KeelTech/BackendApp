from django.db.models import Q

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status as HTTP_STATUS
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError

from keel.authentication.backends import JWTAuthentication
from keel.Core.err_log import log_error
from keel.Core.constants import GENERIC_ERROR
from keel.Core.helpers import generate_unique_id
from keel.tasks.models import Task, TaskComments
from keel.cases.models import Case

from .serializers import (ListTaskSerializer, TaskSerializer, TaskCreateSerializer, 
                            TaskUpdateSerializer, CreateTaskCommentSerializer)


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
        req_data = request.GET.dict()
        case_id = req_data.get("case","")

        # Verify Case Id 
        if not case_id:
            log_error("ERROR", "ListTask: list", str(user_id), err = "invalid case_id")        
            response["message"] = "Invalid Case Id"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        # Validate Request Param Data
        try:
            task_validation = ListTaskSerializer(data = req_data)
            task_validation.is_valid(raise_exception = True) 
            validated_data = task_validation.validated_data
        except ValidationError as e:
            log_error("ERORR","ListTask: list validate_status", str(user_id), err = str(e))
            response["message"] = "Invalid Request Data"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        # validate Case ID against User/Agent
        try:
            Case.objects.get(Q(user = user_id) | Q(agent = user_id), case_id = case_id)
        except Case.DoesNotExist as e:
            log_error("ERROR","ListTask: list", str(user_id), err = str(e), case_id = case_id)
            response["message"] = "Case id does not exist"
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)

        # Filter the data as per req filters
        try:
            tasks = Task.objects.filter(**validated_data)
            task_list_data = ListTaskSerializer(tasks, many = True)
            resp_data = task_list_data.data    
            response['data'] = resp_data 
        except Exception as e:
            log_error("ERROR","ListTask: list ListTaskSerializer", str(user_id), err = str(e))
            response["message"] = GENERIC_ERROR
            response["status"] = 1
            resp_status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status = resp_status)


    def createTask(self, request, format ='json'):

        response = {
            "status" : 0,
            "message" : "Task created successfully",
            "data" : [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        req_data = request.data
        user = request.user
        user_id = user.id
        req_data["user"] = user_id
        req_data["task_id"] = generate_unique_id("task_")

        try:
            task_serializer = TaskCreateSerializer(data = req_data)
            task_serializer.is_valid(raise_exception = True)
            task_obj = task_serializer.save()
            response['data'] = TaskSerializer(task_obj).data

        except ValidationError as e:
            log_error("ERROR","ListTask : createTask", str(user_id), err = str(e))
            response["message"] = GENERIC_ERROR
            response['status'] = 1
            return Response(response, status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status = HTTP_STATUS.HTTP_200_OK)


    def updateTask(self, request, format = 'json', **kwargs):

        response = {
            "status" : 0,
            "message" : "Task updated successfully",
            "data" : [],
        }
        resp_status = HTTP_STATUS.HTTP_200_OK

        req_data = request.data
        user = request.user
        user_id = user.id
        req_data["user"] = user_id

        task_id = kwargs.get("task_id")

        if not task_id:
            log_error("ERROR", "ListTask: updateTask", str(user_id), err_msg = "Invalid Task Id")
            response["message"] = "Task does not exist"
            response["status"] = 1
            return Response(response, status = HTTP_STATUS.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(task_id = task_id)
        except Task.DoesNotExist as e:
            log_error("ERROR", "ListTask: updateTask", str(user_id), err = str(e))
            response["message"] = "Task does not exist"
            response["status"] = 1
            return Response(response, status = HTTP_STATUS.HTTP_400_BAD_REQUEST)

        req_data['task_id'] = task_id
        try:
            task_serializer = TaskUpdateSerializer(task, data = req_data)
            task_serializer.is_valid(raise_exception = True)
            task_obj = task_serializer.save()
            response['data'] = TaskSerializer(task_obj).data

        except ValidationError as e:
            log_error("ERROR","ListTask : updateTask", str(user_id), err = str(e))
            response["message"] = GENERIC_ERROR
            response['status'] = 1
            return Response(response, status = HTTP_STATUS.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status = HTTP_STATUS.HTTP_200_OK)




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
        req_data = request.data

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
            return Response(response, status = HTTP_STATUS.HTTP_400_BAD_REQUEST)

        comment_obj.mark_delete()
        return Response(response, status = resp_status)




