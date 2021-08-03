from django.conf import settings

import requests
from requests.exceptions import ConnectionError, ConnectTimeout
from rest_framework import status
import urllib.parse

from .api_resp_parse import PARSER_FACTORY as parser_factory
from .constants import CALENDLY_API_PATH as api_details

import logging
logger = logging.getLogger('app-logger')


class CalendlyApis(object):

    @staticmethod
    def single_use_scheduling_link(event_type_url: str, invitee_name: str, invitee_email: str):
        response = {
            "status": 0,
            "schedule_link": "",
            "error": ""
        }

        url = settings.CALENDLY_BASE_URL + api_details["single_use_scheduling_link"]
        bearer_token = "Bearer " + settings.CALENDLY_PERSONAL_TOKEN
        header = {
            "authorization": bearer_token,
        }
        payload = {
          "max_event_count": 1,
          "owner": event_type_url,
          "owner_type": "EventType"
        }
        params = urllib.parse.urlencode({
            "name": invitee_name if invitee_name else "",
            "email": invitee_email
        })

        try:
            request_resp = requests.post(url=url, headers=header, data=payload, timeout=5)
            req_resp_json = request_resp.json()
            status_code = request_resp.status_code
            response_parser = parser_factory.get_parser("single_use_scheduling_link")(req_resp_json)
            if status_code == status.HTTP_201_CREATED:
                if response_parser.validate_201():
                    response["schedule_link"] = response_parser.extract_201() + "?" + str(params)
                    response["status"] = 1
                else:
                    response["error"] = response_parser.error()
            elif status_code == status.HTTP_400_BAD_REQUEST:
                response["error"] = "Invalid Request"
            elif status_code == status.HTTP_401_UNAUTHORIZED:
                response["error"] = "Invalid authentication token"
            elif status_code == status.HTTP_403_FORBIDDEN:
                response["error"] = "User not authorize to do the request"
            elif status_code == status.HTTP_404_NOT_FOUND:
                response["error"] = "Requested resource not found"
            elif status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                response["error"] = "Internal error from Calendly"
            return response
        except ConnectionError as e:
            pass
        return response
