from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from .serializers import EligibilityResultsSeriaizer
from keel.eligibility_calculator.models import EligibilityResults
from keel.leads.models import CustomerLead

import logging
logger = logging.getLogger('app-logger')

class EligibilityResultsView(viewsets.GenericViewSet):

    def submit(self, request):
        data = {
                'status' : 1,
                "message" : ''
            }
        serializer = EligibilityResultsSeriaizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        valid_data = serializer.validated_data

        # get name and email from validated data
        get_data = valid_data.get('data', None)
        name = get_data.get('name', None)
        email = get_data.get('email', None)
        lead_source = CustomerLead.WEB

        # create instance of leads with name, email and temporarily lead_source which has a value of "WEB"
        try:
            lead = CustomerLead(name=name, email=email)
            lead.save()
            # add lead id to validated data
            valid_data['lead_id'] = lead
            serializer.save()

        except Exception as e:
            logger.error('ERROR: ELIGIBILITY_CALCULATOR:EligibilityResultsView ' + str(e))
            response['messge'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        response["message"] =  serializer.data 
        
        return Response(response)
