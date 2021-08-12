CALENDLY_API_PATH = {
    "single_use_scheduling_link": "/scheduling_links"
}

CALENDLY_WEBHOOK_PATH = "/webhook_subscriptions"
CALENDLY_WEBHOOK_EVENTS = ["invitee.canceled", "invitee.created"]
CALENDLY_WEBHOOK_SIGNATURE_KEY = "Calendly-Webhook-Signature"

CALENDLY_USERS_URL_PATH = "{}/users/{}"
CALENDLY_EVENT_TYPE_URL_PATH = "{}/event_types/{}"
CALENDLY_EVENT_URL_PATH = "{}/scheduled_events/{}"
CALENDLY_INVITEE_URL_PATH = "{}/scheduled_events/{}/invitees/{}"

CALENDLY_SIGNATURE_TKEY = "t"
CALENDLY_SIGNATURE_VKEY = "v1"
CALENDLY_EVENT_TOLERANCE_TIME = 300000  # in milliseconds
