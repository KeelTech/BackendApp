from keel.authentication.backends import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from .serializers import EligibilityResultsSeriaizer, CrsCalculatorSerializer
from keel.eligibility_calculator.models import EligibilityResults
from keel.leads.models import CustomerLead
from .helpers.crs_calculator import CrsCalculator

import logging
logger = logging.getLogger('app-logger')

class EligibilityResultsView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication, )


    def submit(self, request, format='json'):
        response = {
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
            lead = CustomerLead(name=name, email=email, lead_source=lead_source)
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


class CrsCalculatorView(APIView):

    @classmethod
    def calculate_crs(data):
        
        serializer = CrsCalculatorSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        """
        get payload which are keys to get values from the dictionary, 
        the values are of int type
        """
        
        is_with_spouse = validated_data.get('with_spouse', None)
        education = validated_data.get('education', None)
        language_test = validated_data.get('language_test', None)
        work_experience = validated_data.get('work_experience', None)
        age = validated_data.get('age', None)

        #instantiate crs calculator
        crs_calculator = CrsCalculator(is_with_spouse, education, language_test, work_experience, age)

        # check if is_with_spouse is true, then calculate crs score accordingly
        if is_with_spouse == "true":
            crs_score = crs_calculator.calculate_crs_with_spouse()
        else:
            crs_score = crs_calculator.calculate_crs_without_spouse()
        
        return crs_score

    def post(self, request, format='json'):
        response = {
            'status' : 1,
            "message" : ''
        }
        data = request.data
        
        crs_score = self.calculate_crs(data)
            
        response['message'] = "CRS Score is {}".format(crs_score)
        return Response(response)