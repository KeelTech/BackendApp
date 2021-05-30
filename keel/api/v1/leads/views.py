from rest_framework.views import APIView
from rest_framework.response import Response
from keel.api.permissions import CustomLeadPermission
from rest_framework import status
from .serializers import CustomerLeadSerializer

class CustomerLeadView(APIView):

    # permission_classes = (CustomLeadPermission, )

    def post(self, request, format="json"):
        serializer = CustomerLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        valid_data = serializer.validated_data

        data = {
            "status" : 1,
            "message" : valid_data
        }
        
        return Response(data, status=status.HTTP_201_CREATED)