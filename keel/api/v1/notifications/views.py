from django.core.exceptions import ObjectDoesNotExist
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.notifications.models import InAppNotification
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import InAppNotificationSerializer


class NotificationViews(GenericViewSet):
    serializer_class = InAppNotificationSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_notifications(self, request):
        response = {
            "status": 1,
            "message": "Successfully retrived notification",
            "data": [],
        }

        # check recent query param
        recent = request.query_params.get("recent", None)

        # get user case
        try:
            user_case = Case.objects.filter(user=request.user, is_active=True).first()
        except ObjectDoesNotExist:
            log_error(
                LOGGER_LOW_SEVERITY,
                "NotificationViews:get_notifications",
                request.user.id,
                description="Failed to get user case",
            )
            response["status"] = 0
            return Response(response, status=status.HTTP_200_OK)

        # check if recent is true, then return only last notification
        if recent == "true":
            queryset = (
                InAppNotification.objects.filter(case_id=user_case, seen=False)
                .last()
            )
            if not queryset:
                response["status"] = 0
                response["message"] = "No new notifications"
                return Response(response, status=status.HTTP_200_OK)

            serializer = self.serializer_class(queryset, many=False).data

        # if recent is false, then return all notifications
        else:
            try:
                queryset = (
                    InAppNotification.objects.filter(case_id=user_case, seen=False)
                    .order_by("-created_at")
                )
                serializer = self.serializer_class(queryset, many=True).data
            except Exception as err:
                log_error(
                    LOGGER_LOW_SEVERITY,
                    "NotificationViews:get_notifications",
                    request.user.id,
                    description="An error occured",
                )
                response["message"] = str(err)
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["data"] = serializer
        return Response(response, status=status.HTTP_200_OK)

    def mark_notification_read(self, request, pk):
        response = {"status": 1, "message": "Successfully marked notification as read"}

        try:
            notification = InAppNotification.objects.get(id=pk)
        except ObjectDoesNotExist as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "NotificationViews:mark_notification_read",
                request.user.id,
                description="Failed to get notification",
            )
            response["status"] = 0
            response["message"] = str(err)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "NotificationViews:mark_notification_read",
                request.user.id,
                description="An error occured",
            )
            response["message"] = str(err)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        notification.seen = True
        notification.save()

        return Response(response, status=status.HTTP_200_OK)
