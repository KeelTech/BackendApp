from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.web.models import HomeLeads, WebsiteContactData
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import HomeLeadsSerializer, WebsiteContactDataSerializer
from .utils import LeadSquared


class WebsiteContactDataView(ModelViewSet):
    queryset = WebsiteContactData.objects.all()
    serializer_class = WebsiteContactDataSerializer

    def create(self, request, *args, **kwargs):
        response = {"status": 1, "message": "Message Sent Successfully", "data": {}}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as e:
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # SEND DATA TO LEADSQUARED
        leadsquared = LeadSquared(request.data).send_data_to_leadsquared()
        if leadsquared != 200:
            log_error(
                LOGGER_LOW_SEVERITY,
                "WebsiteContactDataView:create",
                "",
                description="Error in sending data to leadsquared",
            )

        response["data"] = serializer.data
        return Response(response, status=status.HTTP_201_CREATED)


class HomeLeadsView(ModelViewSet):
    queryset = HomeLeads.objects.all()
    serializer_class = HomeLeadsSerializer

    def create(self, request, *args, **kwargs):
        response = {"status": 1, "message": "Message Sent Successfully", "data": {}}
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except Exception as e:
            response["status"] = 0
            response["message"] = str(e)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # SEND DATA TO LEADSQUARED
        leadsquared = LeadSquared(request.data).send_data_to_leadsquared()
        if leadsquared != 200:
            log_error(
                LOGGER_LOW_SEVERITY,
                "WebsiteContactDataView:create",
                "",
                description="Error in sending data to leadsquared",
            )
        response["data"] = serializer.data
        return Response(response, status=status.HTTP_201_CREATED)
