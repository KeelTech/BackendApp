from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.template.loader import get_template

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from keel.authentication.backends import JWTAuthentication

from keel.calendly.utils import calendly_business_logic

import logging
logger = logging.getLogger('app-logger')


class ScheduleCallViewSet(GenericViewSet):

    def get_schedule_page(self, request, **kwargs):
        template = get_template('calendly_landing.html')  # getting our templates
        return HttpResponse(template.render())


class RCICScheduleUrl(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_call_schedule_url(self, request, **kwargs):
        response = {
            'status': 1,
            "message": ''
        }
        try:
            user = request.user
            rcic_email = user.users_cases.get(is_active=True).agent.email
        except ObjectDoesNotExist as err:
            response["status"] = 0
            response["message"] = "Case does not exist for the user"
            return Response(response, status.HTTP_400_BAD_REQUEST)
        except MultipleObjectsReturned as err:
            response["status"] = 0
            response["message"] = "Multiple RCIC assigned to the user"
            return Response(response, status.HTTP_400_BAD_REQUEST)
        schedule_url = calendly_business_logic.get_agent_schedule_url(user.first_name, user.email, rcic_email)

        if not schedule_url:
            response["status"] = 0
            response["message"] = "Error getting schedule url of assigned RCIC"
            return Response(response, status.HTTP_400_BAD_REQUEST)

        response["message"] = {"schedule_url": schedule_url}
        return Response(response, status=status.HTTP_200_OK)
