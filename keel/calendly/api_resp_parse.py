from keel.calendly.models import CalendlyCallSchedule


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


class ScheduleEventInviteeDetailsApi(IApiParseValidateResp):

    def __init__(self, json_api_resp):
        self.api_resp = json_api_resp
        self._error = ""

    def validate_200(self):
        if not self.api_resp.get("resource", {}).get("cancel_url") or \
                not self.api_resp.get("resource", {}).get("reschedule_url"):
            self._error = "Invalid api response"
            return False
        return True

    def extract_200(self):
        resource = self.api_resp["resource"]
        return {
            "cancel_url": resource["cancel_url"],
            "reschedule_url": resource["reschedule_url"],
            "status": resource.get("status"),
            "event_resource_url": resource["event"],
            "timezone": resource.get("timezone"),
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
                or not "location" not in self.api_resp["resource"] \
                or not self.api_resp["resource"].get("status") or \
                "rescheduled" not in self.api_resp["resource"]:
            self._error = "Invalid api response"
            return False
        return True

    def extract_200(self):
        resource = self.api_resp["resource"]
        return {
            "status": CalendlyCallSchedule.CALL_SCHEDULE_MAP.get(str(resource["status"]).lower()),
            "location": resource["location"],
            "start_time_utc": resource["start_time"],
            "end_time_utc": resource["end_time"],
            "new_invitee": resource.get("new_invitee"),
            "rescheduled": resource["rescheduled"],
            "event_invitee_url": resource["uri"]
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
