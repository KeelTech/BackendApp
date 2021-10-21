import logging

from django.db.models import manager, query
from django.http import response
from keel.authentication.backends import JWTAuthentication
from keel.cases.models import Case
from keel.plans.models import Plan
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import PlanSerializers, PlatformComponentsSerializer

logger = logging.getLogger('app-logger')


class PlanListView(GenericViewSet):
    serializer_class = PlanSerializers
    permission_classes = (permissions.AllowAny, )
    authentication_classes = (JWTAuthentication, )

#     def create_plan(self, request):
#         response = {'status' : 1, 'message' : "Plans retrieved successfully", 'data' : ""}
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         validated_data = serializer.validated_data
#         try:
#             serializer.save()
#         except:
#             pass
#         return Response()
    
    def list_plans(self, request):
        response = {'status' : 1, 'message' : "Plans retrieved successfully", 'data' : ""}
        queryset = Plan.objects.filter(is_active=True)
        serializer = self.serializer_class(queryset, many=True).data
        response['data'] = serializer
        return Response(response)


class PlanDetailView(GenericViewSet):
    serializer_class = PlanSerializers
    permission_classes = (permissions.AllowAny, )
    authentication_classes = (JWTAuthentication, )
    
    def plan_details(self, request, **kwargs):
        response = {'status' : 1, 'message' : "Plans retrieved successfully", 'data' : ""}
        plan_id = kwargs.get('id')
        try:
            queryset = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist as e:
            logger.error('ERROR: PLAN:PlanDetailView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(queryset).data
        discount_price = queryset.get_discount_price()
        serializer['discount_price'] = discount_price
        
        #cehck if price is more than zero and return free or paid plna type
        # if queryset.price > 0:
        #     serializer['plan_type'] = "Paid"
        # else:
        #     serializer['plan_type'] = "Free"

        response['data'] = serializer
        return Response(response)


class PlanComponentsView(GenericViewSet):
    serializer_class = PlatformComponentsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_plan_component(self, request):
        response = {'status':1, "message":""}
        
        try:
            case = Case.objects.get(user=request.user, is_active=True)
            plan = Plan.objects.get(title=case.plan).platform_components.all()
        except Exception as e:
            logger.error('ERROR: PLAN:PlanComponentsView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(plan, many=True).data
        response["message"] = serializer
        return Response(response)
