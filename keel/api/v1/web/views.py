import imp

from keel.web.models import HomeLeads, WebsiteComponents, WebsiteContactData
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import (HomeLeadsSerializer, WebsiteComponentsSerializer,
                          WebsiteContactDataSerializer)


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


class WebsiteComponentsView(ModelViewSet):
    queryset = WebsiteComponents.objects.all()
    serializer_class = WebsiteComponentsSerializer

    def list(self, request):
        serializer = self.get_serializer(self.queryset.all(), many=True)
        return Response(serializer.data)