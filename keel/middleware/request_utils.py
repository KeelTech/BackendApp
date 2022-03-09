from threading import current_thread
from django.utils.deprecation import MiddlewareMixin

_requests = {}


def get_current_request():
    return _requests.get(current_thread().ident)



class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _requests[current_thread().ident] = request

    def process_response(self, request, response):
        del _requests[current_thread().ident]
        return response