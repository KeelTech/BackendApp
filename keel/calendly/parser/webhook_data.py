from keel.calendly.models import CalendlyCallSchedule, CallSchedule
from .invitee_validator import ScheduleInviteeValidator


class CalendlyWebHookDataParser(ScheduleInviteeValidator):
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
        if not self.validate_invitee_data(payload):
            return False
        return True

    def parse_extract_data(self):
        payload = self.webhook_data["payload"]
        return {
            "event": self.event,
            "invitee_url_to_update": payload["old_invitee_url"] or payload["uri"] or payload["new_invitee_url"]
        }

    @property
    def event(self):
        return self.webhook_data.get("event")

    @property
    def error(self):
        return self._error
