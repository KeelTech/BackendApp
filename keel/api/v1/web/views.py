from keel.web.models import HomeLeads, WebsiteComponents, WebsiteContactData, IeltsData, JobPostingData
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    BlogListSerializer,
    HomeLeadsSerializer,
    WebsiteComponentsSerializer,
    WebsiteContactDataSerializer,
    IeltsListSerializer,
    JobsPostingListSerializer
)


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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BlogListView(ModelViewSet):
    serializer_class = WebsiteComponentsSerializer

    def get_queryset(self, pk=None):
        if pk:
            return WebsiteComponents.objects.filter(id=pk)

        return WebsiteComponents.objects.filter(
            component_name=WebsiteComponents.BLOGS, is_active=True
        ).order_by('-updated_at')

    def list(self, request):
        response = {
            "status": 1,
            "message": "Successfully retrived blog list",
            "data": {},
        }
        queryset = self.get_queryset()
        serializer = BlogListSerializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        response = {
            "status": 1,
            "message": "Successfully retrived blog details",
            "data": {},
        }
        queryset = self.get_queryset(pk=pk)
        serializer = self.get_serializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

class IeltsListView(ModelViewSet):
    queryset = IeltsData.objects.all()
    serializer_class = IeltsListSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class JobPostingListView(ModelViewSet):
    queryset = JobPostingData.objects.all()
    serializer_class = JobsPostingListSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)