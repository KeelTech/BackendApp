from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import EligibilityResultsSeriaizer
from keel.eligibility_calculator.models import EligibilityResults
from keel.leads.models import CustomerLead

class EligibilityResultsView(APIView):

    def post(self, request, format='json'):
        serializer = EligibilityResultsSeriaizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        valid_data = serializer.validated_data

        # get name and email from validated data
        name = valid_data['data']['name']
        email = valid_data['data']['email']

        # create instance of leads with name, email and temporarily lead_source = 1 which has a value of "WEB"
        lead = CustomerLead(name=name, email=email, lead_source=1)
        lead.save()

        # add lead id to validated data
        valid_data['lead_id'] = lead

        serializer.save()
        
        response = {
            "status" : 1,
            "message" : serializer.data 
        }
        return Response(response, status=status.HTTP_201_CREATED)
