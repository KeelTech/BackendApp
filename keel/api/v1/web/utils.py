import json

import requests
from django.conf import settings
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error

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
        return response


class VerifyLeadSquaredResponse(object):
    def __init__(self, response, model, obj, data):
        self.response = response
        self.obj = obj
        self.data = data
        self.model = model

    def check_response(self):
        if self.response.status_code == 200:
            return self.check_200()
        if self.response.status_code == 500:
            return self.check_500()

        return True

    def check_200(self):
        resp_text = json.loads(self.response.text)
        if resp_text["Status"] == "Success":
            self.obj.leadsquared_id = resp_text["Message"]["Id"]
            self.obj.leadsquared_status_code = self.response.status_code
            self.obj.save()

        return True

    def check_500(self):
        resp_text = json.loads(self.response.text)
        if resp_text["ExceptionType"] == "MXDuplicateEntryException":
            try:
                get_instance_with_leadsqaured_id = self.model.objects.filter(
                    **self.data
                ).first()
                if get_instance_with_leadsqaured_id.leadsquared_id:
                    self.obj.leadsquared_id = (
                        get_instance_with_leadsqaured_id.leadsquared_id
                    )
                    self.obj.leadsquared_status_code = self.response.status_code
                    self.obj.save()
            except Exception as err:
                log_error(
                    LOGGER_LOW_SEVERITY,
                    "VerifyLeadSquaredResponse:check_500",
                    "",
                    description="Error in updating leadsquared id",
                )

        return True
