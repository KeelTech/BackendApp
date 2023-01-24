from keel.web.models import HomeLeads, WebsiteComponents, WebsiteContactData
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
import requests, json

from .serializers import (
    BlogListSerializer,
    HomeLeadsSerializer,
    WebsiteComponentsSerializer,
    WebsiteContactDataSerializer,
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
            "message": "Successfully retrieved blog list",
            "data": {},
        }
        queryset = self.get_queryset()
        serializer = BlogListSerializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response)

    def retrieve(self, request, pk=None):
        response = {
            "status": 1,
            "message": "Successfully retrived blog details",
            "data": {},
        }
        queryset = self.get_queryset(pk=pk)
        serializer = self.get_serializer(queryset, many=True)
        response["data"] = serializer.data
        return Response(response)


class LeadEngine(GenericViewSet):

    def push_leadsquared(self, request):
        resp = {'status': 0,
                'message': ''}

        access_key = 'u$r7d916217a5676919cdd9cf6b050e63e7'
        secret_key = '0dc2429e937f9742fd2153e955d0483ed9a426cb'
        url = 'https://asyncapi-in21.leadsquared.com/lead/capture?accessKey='+access_key+'&secretKey='+secret_key

        # url = "https://api-in21.leadsquared.com/v2/LeadManagement.svc/Lead.Capture?accessKey="+access_key+"&secretKey="+secret_key
        headers_obj = {'x-api-key': 'ZMy4nAMclj8hnKpGQg7DD369ZRNj0Oqy3fZ5Wczl', "Content-Type": "application/json"}
        # headers_obj = {"Content-Type": "application/json"}
        req_body = request.data

        req_obj = requests.post(url, json=req_body)

        if req_obj.status_code in (200, 201):
            print(req_obj.text)
            resp['status'] = 1
        return Response(resp)


