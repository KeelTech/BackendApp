import logging

from keel.api.permissions import IsRCICUser
from keel.api.v1.auth.serializers import (
    BaseProfileSerializer,
    CustomerQualificationsSerializer,
    CustomerWorkExperienceSerializer,
    UserDetailsSerializer,
)
from django.db.models import Prefetch
from keel.api.v1.chats.views import ChatList
from keel.api.v1.tasks.instances import number_of_tasks_per_status
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import AgentNotes, Case, Program
from keel.Core.err_log import log_error
from keel.tasks.models import Task
from rest_framework import generics, permissions, response, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from keel.chats.models import ChatReceipts, ChatRoom, Chat
from .serializers import (
    AgentNoteSerializer,
    BaseCaseProgramSerializer,
    BaseCaseSerializer,
    CaseIDSerializer,
    CaseProgramSerializer,
    CasesSerializer,
    CaseTrackerSerializer,
)
from .utils import sort_case_chat_list

logger = logging.getLogger("app-logger")


class CaseView(generics.CreateAPIView):
    serializer_class = CasesSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Case.objects.all()


class FilterUserCases(generics.ListAPIView):
    serializer_class = CasesSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)

    def get(self, request):
        response = {"status": 1, "message": ""}
        user = request.user
        req_data = request.GET.dict()
        queryset = Case.objects.get_agent_cases(user, req_data)
        serializer = self.serializer_class(queryset, many=True)
        response["message"] = serializer.data
        return Response(response)


class CaseUnreadChats(generics.ListAPIView):

    serializer_class = BaseCaseSerializer
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        response = {"status": 1, "message": ""}
        user = request.user
        queryset = (
            Case.objects.select_related("user__user_profile", "agent")
            .prefetch_related(
                Prefetch(
                    "case_chats_receipts",
                    queryset=ChatReceipts.objects.select_related("user_id", "chat_id"),
                ),
                Prefetch(
                    "cases_chatrooms",
                    queryset=ChatRoom.objects.select_related("user", "agent"),
                ),
                "cases_chatrooms__chatroom_chats",
            )
            .filter(agent=user)
        )
        serializer = self.serializer_class(queryset, many=True).data

        # sort case chat list
        sorted_list = sort_case_chat_list(serializer)

        response["message"] = sorted_list
        return Response(response)


class FilterUserCasesDetails(GenericViewSet):

    serializer_class = CasesSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_case(self, request, **kwargs):
        response = {"status": 1, "message": ""}
        pk = kwargs.get("case_id")
        try:
            queryset = (
                Case.objects.select_related("user")
                .prefetch_related(
                    "agent_case_notes",
                    "cases_tasks",
                    "case_chats_receipts",
                    "cases_chatrooms",
                )
                .get(case_id=pk, is_active=True)
            )
            serializer_cases = self.serializer_class(queryset)

            # get all user qualifications
            qualifications = queryset.user.user_qualification.all()
            serializer_qua = CustomerQualificationsSerializer(qualifications, many=True)

            # get all user work experiences
            work_experinece = queryset.user.user_workexp.all()
            serializer_work = CustomerWorkExperienceSerializer(
                work_experinece, many=True
            )

            # get user profile
            serializer_profile = BaseProfileSerializer(queryset.user.user_profile)

            # get number of tasks related to cases from Task Model
            tasks = number_of_tasks_per_status(queryset)

            # get agent notes
            last = queryset.agent_case_notes.all()
            agent_notes = last[len(last) - 1] if last else None
            serializer_agent_notes = AgentNoteSerializer(agent_notes)

            data = {
                "case_details": serializer_cases.data,
                "user_qualifications": serializer_qua.data,
                "user_work_experience": serializer_work.data,
                "user_details": serializer_profile.data,
                "task_count": tasks["tasks"],
                "pending_task_count": tasks["pending_tasks"],
                "in_review_task_count": tasks["in_review_tasks"],
                "completed_task_count": tasks["completed_tasks"],
                "agent_notes": serializer_agent_notes.data,
            }
        except Exception as e:
            logger.error("ERROR: CASE:FilterUserCasesDetails " + str(e))
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        response["message"] = data
        return Response(response)


class UpdateCaseProgramView(GenericViewSet):
    serializer_class = CaseProgramSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_all_programs(self, request):
        response = {"status": 1, "message": "All programs retreived", "data": ""}
        queryset = Program.objects.all()
        serializer = BaseCaseProgramSerializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response)

    def update_program(self, request, **kwargs):
        response = {"status": 1, "message": "Program Updated successfully", "data": ""}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        program = serializer.validated_data
        case_id = kwargs.get("case_id")
        user_id = request.user.id

        # check case id belongs to request.user and return case obj
        case_serializer = CaseIDSerializer(
            data={"case_id": case_id, "user_id": user_id}
        )
        case_serializer.is_valid(raise_exception=True)
        case_obj = case_serializer.validated_data

        try:
            # get case obj
            case = Case.objects.get(case_id=case_obj, is_active=True)
            case.program = program
            case.save()
        except Case.DoesNotExist as e:
            logger.error("ERROR: CASE:UpdateCaseProgramView " + str(e))
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("ERROR: CASE:UpdateCaseProgramView " + str(e))
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        case_serializer = CasesSerializer(case)
        response["data"] = case_serializer.data
        return Response(response)


class AgentNotesViewSet(GenericViewSet):
    serializer_class = AgentNoteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsRCICUser)

    def create_agent_notes(self, request):
        response = {
            "status": 1,
            "message": "Agent Notes Created Successfully",
            "data": "",
        }
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent = request.user

        # get agent case obj from query param
        case = Case.objects.get(
            case_id=request.query_params.get("case_id"), is_active=True
        )
        data = serializer.validated_data
        data["case"] = case
        data["agent"] = agent

        # check if agent already has note for this case and update it
        agent_note = AgentNotes.objects.filter(case=case, agent=agent).first()

        if agent_note:
            agent_note.title = serializer.validated_data.get("title")
            agent_note.notes = serializer.validated_data.get("notes")
            agent_note.save()
            serializer = self.serializer_class(agent_note).data
            response["message"] = "Agent Notes Updated Successfully"
            response["data"] = serializer
            return Response(response)

        else:
            try:
                serializer.save()
            except Exception as e:
                logger.error("ERROR: CASE:AgentNotesViewSet " + str(e))
                response["message"] = str(e)
                response["status"] = 0
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            response["data"] = serializer.data
            return Response(response, status=status.HTTP_201_CREATED)


class CaseTrackerView(GenericViewSet):
    serializer_class = CaseTrackerSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_case_tracker(self, request):
        response = {"status": 1, "message": "Case Tracker retreived", "data": ""}
        user = request.user
        try:
            case = Case.objects.prefetch_related(
                "case_tracker", "case_tracker__case_checkpoint"
            ).get(user=user, is_active=True)
            queryset = case.case_tracker.all()
            serializer = CaseTrackerSerializer(queryset, many=True)
        except Case.DoesNotExist as e:
            logger.error("ERROR: CASE:CaseTrackerView " + str(e))
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("ERROR: CASE:CaseTrackerView " + str(e))
            response["message"] = str(e)
            response["status"] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["data"] = serializer.data
        return Response(response)
