from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from keel.Core.constants import LOGGER_CRITICAL_SEVERITY
from keel.Core.err_log import logging_format

import logging
logger = logging.getLogger('app-logger')


class RequestErrorLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        error_message = "Unhandled error raised while processing request path - {} " \
                        "with exception - {}".format(request.path_info, exception)
        logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "MiddleWare", request.user, description=error_message))
        return HttpResponse("Internal Error occurred", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
