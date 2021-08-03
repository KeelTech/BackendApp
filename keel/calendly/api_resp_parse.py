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


class ApiResponseParsingFactory(object):
    api_parsers = {
        "single_use_scheduling_link": SingleSchedulingLinkApi
    }

    def get_parser(self, api_name):
        return self.api_parsers[api_name]

PARSER_FACTORY = ApiResponseParsingFactory()
