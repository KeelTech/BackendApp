
class ScheduleInviteeValidator(object):

    def validate_invitee_data(self, data):
        required_keys = ("uri", "canceled", "rescheduled", "reschedule_url", "cancel_url", "event",
                         "new_invitee", "old_invitee", "status")
        for key in required_keys:
            if key not in data:
                return False
        return True
