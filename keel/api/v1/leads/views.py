from rest_framework.views import APIView
from rest_framework.response import Response
from keel.api.permissions import CustomLeadPermission
from rest_framework import status
from .serializers import CustomerLeadSerializer

import logging

logger = logging.getLogger('app-logger')
class CustomerLeadView(APIView):

    # permission_classes = (CustomLeadPermission, )

    def post(self, request, format="json"):
        serializer = CustomerLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
        except Exception as e:
            logger.warning('ERROR: LEADS:CustomerLeadView ' + str(e))
            data = {
                'status' : 0,
                "message" : str(e)
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        response = {
            "status" : 1,
            "message" : serializer.data
        }
        return Response(response)