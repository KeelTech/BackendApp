class IApiParseValidateResp(object):

    def validate_200(self):
        raise NotImplementedError

    def extract_200(self):
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


class ScheduleEventInviteeDetailsApi(IApiParseValidateResp):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_201(self):
        if not self.api_resp.get("cancel_url") or not self.api_resp.get("reschedule_url"):
            self._error = "Invalid api response"
            return False
        return True

    def extract_201(self):
        return {
            "cancel_url": self.api_resp["cancel_url"],
            "reschedule_url": self.api_resp["reschedule_url"],
            "status": self.api_resp.get("status"),
            "event_resource_url": self.api_resp["event"],
            "timezone": self.api_resp.get("timezone"),
        }

    def error(self):
        return self._error


class ScheduleEventDetialsApi(IApiParseValidateResp):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_201(self):
        if not self.api_resp.get("start_time") or not self.api_resp.get("end_time") \
                or not self.api_resp.get("location"):
            self._error = "Invalid api response"
            return False
        return True

    def extract_201(self):
        return {
            "status": self.api_resp.get("status"),
            "location": self.api_resp["location"],
            "start_time_utc": self.api_resp["start_time"],
            "end_time_utc": self.api_resp["end_time"],
        }

    def error(self):
        return self._error


class ApiResponseParsingFactory(object):
    api_parsers = {
        "single_use_scheduling_link": SingleSchedulingLinkApi,
        "schedule_event_invitee_details": ScheduleEventInviteeDetailsApi,
        "schedule_event_details": ScheduleEventDetialsApi
    }

    def get_parser(self, api_name):
        return self.api_parsers[api_name]

PARSER_FACTORY = ApiResponseParsingFactory()
