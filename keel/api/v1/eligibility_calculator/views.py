from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from .serializers import EligibilityResultsSeriaizer, CrsCalculatorSerializer
from keel.eligibility_calculator.models import EligibilityResults
from keel.leads.models import CustomerLead
from .helpers import score_dict

import logging
logger = logging.getLogger('app-logger')

class EligibilityResultsView(viewsets.GenericViewSet):


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


class CrsCalculatorView(APIView):

    def post(self, request, format='json'):
        response = {
            'status' : 1,
            "message" : ''
        }
        serializer = CrsCalculatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # check if request is ajax and post
        validated_data = serializer.validated_data

        # get payload which are keys to get values from the dictionary, 
        # the values are of int type
        with_spouse = validated_data.get('with_spouse', None) #assuming this is a boolean, with_spouse = 1, else 0
        education = validated_data.get('education', None)
        language_test = validated_data.get('language_test', None)
        work_experince = validated_data.get('work_experince', None)
        age = validated_data.get('age', None)

        if with_spouse == '1':
            # each of this variables should return an integer
            get_education = score_dict.EDUCATION_LEVEL_WITH_SPOUSE.get(education, None)
            get_language_test = (score_dict.FIRST_LANGUAGE_PROFICIENCY_WITH_SPOUSE.get(language_test, None) * 4 )
            get_age = score_dict.AGE_WITH_SPOUSE.get(age, None)
            get_work_experince = score_dict.WORK_EXPERIENCE_WITH_SPOUSE.get(work_experince, None)
            
            # perform calculation with addition operation
            try:
                crs_score = (get_education + get_language_test + get_age + get_work_experince)
            except ValueError as e:
                logger.warning('ERROR: ELIGIBILITY_CALCULATOR:CrsCalculatorView ' + str(e))
                response['status'] = 0
                response['messagae'] = str(e)
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            response['message'] = crs_score
            return Response(response)
        
        else:
            # each of this variables should return an integer
            get_education = score_dict.EDUCATION_LEVEL_WITHOUT_SPOUSE.get(education, None)
            get_language_test = (score_dict.FIRST_LANGUAGE_PROFICIENCY_WITHOUT_SPOUSE.get(language_test, None) * 4 )
            get_age = score_dict.AGE_WITHOUT_SPOUSE.get(age, None)
            get_work_experince = score_dict.WORK_EXPERIENCE_WITHOUT_SPOUSE.get(work_experince, None)
            
            # perform calculation with addition operation
            try:
                crs_score = (get_education + get_language_test + get_age + get_work_experince)
            
            except ValueError as e:
                logger.warning('ERROR: ELIGIBILITY_CALCULATOR:CrsCalculatorView ' + str(e))
                response['status'] = 0
                response['messagae'] = str(e)
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            response['message'] = crs_score
            return Response(response)