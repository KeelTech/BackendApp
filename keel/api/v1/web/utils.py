import requests
from django.conf import settings

LEADSQUARED_URL = settings.LEADSQUARED_URL
LEADSQUARED_ACCESS_KEY = settings.LEADSQUARED_ACCESS_KEY
LEADSQUARED_SECRET_KEY = settings.LEADSQUARED_SECRET_KEY


class LeadSquared(object):
    def __init__(self, data):
        self.data = data

    def format_data(self):

        data = [
            {"Attribute": "FirstName", "Value": "" + self.data.get("name", "")},
            {"Attribute": "EmailAddress", "Value": "" + self.data.get("email", "")},
            {"Attribute": "Phone", "Value": "" + self.data.get("phone", "")},
            {"Attribute": "Notes", "Value": "" + self.data.get("message", "")},
        ]

        return data

    def send_data_to_leadsquared(self):
        url = (
            LEADSQUARED_URL
            + "?accessKey="
            + LEADSQUARED_ACCESS_KEY
            + "&secretKey="
            + LEADSQUARED_SECRET_KEY
        )
        data = self.format_data()
        response = requests.post(url, json=data)
        print("Response status from leadsquared: ", response.status_code)
        return response.status_code
