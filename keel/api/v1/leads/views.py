from rest_framework.views import APIView
from rest_framework.response import Response
from keel.api.permissions import CustomLeadPermission
from rest_framework import status
from .serializers import CustomerLeadSerializer
from rest_framework import viewsets, mixins, status

import logging
logger = logging.getLogger('app-logger')



class CustomerLeadView(viewsets.GenericViewSet):

    # permission_classes = (CustomLeadPermission, )

    def create(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = CustomerLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: LEADS:CustomerLeadView ' + str(e))
            response['messge'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["message"] =  serializer.data 
        return Response(response)

