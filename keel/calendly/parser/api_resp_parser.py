from keel.calendly.models import CalendlyCallSchedule, CallSchedule
from .invitee_validator import ScheduleInviteeValidator


class IApiParseValidateResp(object):

    def validate_200(self):
        raise NotImplementedError

    def extract_200(self):
        raise NotImplementedError

    def validate_201(self):
        raise NotImplementedError

    def extract_201(self):
        raise NotImplementedError


class SingleSchedulingLinkApi(IApiParseValidateResp):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_201(self):
        if not self.api_resp.get("resource") or not self.api_resp["resource"].get("booking_url"):
            self._error = "Invalid api response"
            return False
        return True

    def extract_201(self):
        return self.api_resp["resource"]["booking_url"]

    def error(self):
        return self._error


class ScheduleInviteeDetailsApi(IApiParseValidateResp, ScheduleInviteeValidator):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_200(self):
        if not self.api_resp.get("resource") or self.validate_invitee_data(self.api_resp["resource"]):
            self._error = "Invalid api response"
            return False
        return True

    def extract_200(self):
        resource = self.api_resp["resource"]
        status = CalendlyCallSchedule.CALL_SCHEDULE_MAP.get(str(resource["status"]).lower())
        status = CallSchedule.RESCHEDULED if resource["new_invitee"] or resource["old_invitee"] else status
        return {
            "cancel_url": resource["cancel_url"],
            "reschedule_url": resource["reschedule_url"],
            "status": status,
            "event_resource_url": resource["event"],
            "timezone": resource.get("timezone"),
            "rescheduled": resource["rescheduled"],
            "invitee_url": resource["uri"],
            "new_invitee_url": resource["new_invitee"]
        }

    def error(self):
        return self._error


class ScheduleEventDetialsApi(IApiParseValidateResp):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_200(self):
        if not self.api_resp.get("resource") \
                or not self.api_resp["resource"].get("start_time") \
                or not self.api_resp["resource"].get("end_time") \
                or "location" not in self.api_resp["resource"]:
            self._error = "Invalid api response"
            return False
        return True

    def extract_200(self):
        resource = self.api_resp["resource"]
        return {
            "location": resource["location"],
            "start_time_utc": resource["start_time"],
            "end_time_utc": resource["end_time"]
        }

    def error(self):
        return self._error


class ApiResponseParsingFactory(object):
    api_parsers = {
        "single_use_scheduling_link": SingleSchedulingLinkApi,
        "schedule_invitee_details": ScheduleInviteeDetailsApi,
        "schedule_event_details": ScheduleEventDetialsApi
    }

    def get_parser(self, api_name):
        return self.api_parsers[api_name]


PARSER_FACTORY = ApiResponseParsingFactory()
