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
    def single_use_scheduling_link(event_type_url: str, call_schedule_number: int, invitee_name: str, invitee_email: str):
        response = {
            "status": 0,
            "schedule_url": "",
            "error": ""
        }

        url = settings.CALENDLY_BASE_URL + api_details["single_use_scheduling_link"]
        bearer_token = "Bearer " + settings.CALENDLY_PERSONAL_TOKEN
        header = {
            "authorization": bearer_token,
        }
        payload = {
          "max_event_count": call_schedule_number,
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
                    response["schedule_url"] = response_parser.extract_201() + "?" + str(params)
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

    @staticmethod
    def get_invitee_details(invitee_url):
        response = {
            "status": 0,
            "data": {"rescheduled": True},
            "error": ""
        }
        bearer_token = "Bearer " + settings.CALENDLY_PERSONAL_TOKEN
        headers = {
            "authorization": bearer_token,
        }
        try:
            while not response["error"] and response["data"]["rescheduled"]:
                request_resp = requests.get(url=invitee_url, headers=headers)
                req_resp_json = request_resp.json()
                status_code = request_resp.status_code
                response_parser = parser_factory.get_parser("schedule_event_invitee_details")(req_resp_json)
                if status_code == status.HTTP_200_OK:
                    if response_parser.validate_200():
                        response["data"] = response_parser.extract_200()
                        response["status"] = 1
                        invitee_url = response["data"].get("new_invitee_url")
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
        except ConnectionError as e:
            pass
        return response

    @staticmethod
    def get_event_details(event_url):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        bearer_token = "Bearer " + settings.CALENDLY_PERSONAL_TOKEN
        headers = {
            "authorization": bearer_token,
        }
        try:
            request_resp = requests.get(url=event_url, headers=headers)
            req_resp_json = request_resp.json()
            status_code = request_resp.status_code
            response_parser = parser_factory.get_parser("schedule_event_details")(req_resp_json)
            if status_code == status.HTTP_200_OK:
                if response_parser.validate_200():
                    response["data"] = response_parser.extract_200()
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

