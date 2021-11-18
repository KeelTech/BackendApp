from django.core.exceptions import ObjectDoesNotExist
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from keel.Core.err_log import log_error
from keel.Core.constants import LOGGER_LOW_SEVERITY
from rest_framework.permissions import IsAuthenticated
from keel.authentication.backends import JWTAuthentication
from keel.notifications.models import InAppNotification

from .serializers import InAppNotificationSerializer

class NotificationViews(GenericViewSet):
    serializer_class = InAppNotificationSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_notifications(self, request):
        response = {'status':1, 'message':'Successfully retrived notification', 'data':''}

        try:
            user_case = request.user.users_cases.get(user=request.user)
            queryset = InAppNotification.objects.filter(case_id=user_case, seen=False).exclude(user_id=request.user)
        except ObjectDoesNotExist as err:
            log_error(LOGGER_LOW_SEVERITY, "NotificationViews:get_notifications", request.user.id,
                                description="Failed to get case for user")
            response['status'] = 0
            response['message'] = str(err)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            log_error(LOGGER_LOW_SEVERITY, "NotificationViews:get_notifications", request.user.id,
                                description="An error occured")
            response['message'] = str(err)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = self.serializer_class(queryset, many=True).data
        response['data'] = serializer
        return Response(response, status=status.HTTP_200_OK)
    
    def mark_notification_read(self, request, pk):
        response = {'status':1, 'message':'Successfully marked notification as read'}

        try:
            notification = InAppNotification.objects.get(id=pk)
        except ObjectDoesNotExist as err:
            log_error(LOGGER_LOW_SEVERITY, "NotificationViews:mark_notification_read", request.user.id,
                                description="Failed to get notification")
            response['status'] = 0
            response['message'] = str(err)
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            log_error(LOGGER_LOW_SEVERITY, "NotificationViews:mark_notification_read", request.user.id,
                                description="An error occured")
            response['message'] = str(err)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        notification.seen = True
        notification.save()

        return Response(response, status=status.HTTP_200_OK)
