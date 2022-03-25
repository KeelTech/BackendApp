import imp
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import WebsiteContactDataSerializer, HomeLeadsSerializer
from keel.web.models import HomeLeads, WebsiteContactData


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
        response["data"] = serializer.data
        return Response(response, status=status.HTTP_201_CREATED)
