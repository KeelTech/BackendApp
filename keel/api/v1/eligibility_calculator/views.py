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
        get_data = valid_data.get('data', None)
        name = get_data.get('name', None)
        email = get_data.get('email', None)
        lead_source = CustomerLead.LEAD_SOURCE

        # create instance of leads with name, email and temporarily lead_source which has a value of "WEB"
        lead = CustomerLead(name=name, email=email, lead_source=lead_source[0][0])
        lead.save()

        # add lead id to validated data
        valid_data['lead_id'] = lead

        serializer.save()
        
        response = {
            "status" : 1,
            "message" : serializer.data 
        }
        return Response(response, status=status.HTTP_200_OK)
