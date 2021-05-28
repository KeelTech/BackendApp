from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .permissions import CustomLeadPermission
from keel.leads.models import CustomerLead
from keel.leads.serializers import CustomerLeadSerializer

class CustomerLeadView(APIView):

    permission_classes = (CustomLeadPermission, )

    def post(self, request, format="json"):
        serializer = CustomerLeadSerializer(data=request.data)

        if not serializer.is_valid():

            data = {
                "status" : 0,
                "message" : serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        custom_lead = serializer.save()

        if not custom_lead:

            data = {
                "status" : 0,
                "message" : serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            "status" : 1,
            "message" : serializer.data
        }
        
        return Response(data, status=status.HTTP_201_CREATED)
