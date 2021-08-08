from django.conf import settings

from keel.calendly.constants import CALENDLY_EVENT_URL_PATH, CALENDLY_EVENT_TYPE_URL_PATH, \
    CALENDLY_INVITEE_URL_PATH, CALENDLY_USERS_URL_PATH
from keel.calendly.models import CalendlyCallSchedule, CallSchedule

class CalendlyWebHookDataParser(object):
    def __init__(self, webhook_data):
        self.webhook_data = webhook_data
        self._error = ""

    def is_valid_data(self):
        if not isinstance(self.webhook_data, dict):
            self._error = "Invalid Web hook data type"
            return False
        if not self.webhook_data.get("event") or not self.webhook_data.get("payload"):
            self._error = "Event or Payload not present"
            return False
        payload = self.webhook_data["payload"]
        if not payload.get("event_type") or not payload.get("event") \
                or not payload.get("invitee") or "new_invitee" not in payload \
                or "old_invitee" not in payload:
            self._error = "Event or Event Type or Invitee or new/old Invitee not present in Payload"
            return False
        if not self.validate_event_type(payload["event_type"]) \
                or not self.validate_event(payload["event"]) \
                or not self.validate_invitee(payload["invitee"]):
            return False
        return True

    def validate_event_type(self, data):
        if not data.get("owner") or not data.get("uuid"):
            self._error = "Owner or uuid not present in Event Type data"
            return False
        owner = data["owner"]
        if not owner.get("uuid"):
            self._error = "Owner does not have uuid in Event Type data"
            return False
        return True

    def validate_event(self, data):
        if not data.get("uuid") or not data.get("start_time") or not data.get("end_time"):
            self._error = "UUID or start_time or end_time not present in Event data"
            return False
        return True

    def validate_invitee(self, data):
        if not data.get("uuid") or "is_reschedule" not in data or "canceled" not in data:
            self._error = "UUID or is_reschedule or canceled not present in Invitee data"
            return False
        return True

    def parse_extract_data(self):
        payload = self.webhook_data["payload"]
        event_type_data = payload["event_type"]
        event_data = payload["event"]
        invitee_data = payload["invitee"]
        base_url = settings.CALENDLY_BASE_URL
        if invitee_data["canceled"]:
            status = CallSchedule.CANCELED
        elif invitee_data["is_reschedule"]:
            status = CallSchedule.RESCHEDULED
        else:
            status = CallSchedule.ACTIVE
        return {
            "user_url": CALENDLY_USERS_URL_PATH.format(base_url, event_type_data["owner"]["uuid"]),
            "event_type_url": CALENDLY_EVENT_TYPE_URL_PATH.format(base_url, event_type_data["uuid"]),
            "event_url": CALENDLY_EVENT_URL_PATH.format(base_url, event_data["uuid"]),
            "invitee_url": CALENDLY_INVITEE_URL_PATH.format(base_url, event_data["uuid"], invitee_data["uuid"]),
            "start_time": event_data["start_time"],
            "end_time": event_data["end_time"],
            "rescheduled": invitee_data["is_reschedule"],
            "canceled": invitee_data["canceled"],
            "status": status,
            "new_invitee_url": payload["new_invitee"],
            "old_invitee_url": payload["old_invitee"]
        }

    @property
    def event(self):
        return self.webhook_data.get("event")

    @property
    def error(self):
        return self._error
