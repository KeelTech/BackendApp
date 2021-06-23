import datetime

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.db.models import F, Sum, Max, Q, Prefetch, Case, When, Count, Value
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins, viewsets, status

from keel.api.v1.auth import serializers
from keel.document.models import Documents
from keel.document.exceptions import *

from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from keel.api.v1.auth import serializers
# from keel.authentication.models import (OtpVerifications, )

import logging
logger = logging.getLogger('app-logger')

User = get_user_model()


class UserViewset(GenericViewSet):

    permission_classes = (AllowAny, )
    serializer_class = serializers.UserRegistrationSerializer

    def signup(self, request, format="json"):
        response = {
            'status' : 1,
            "message" : ''
        } 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
            response['messge'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response["message"] =  serializer.data 
        return Response(response)


class LoginViewset(GenericViewSet):
    serializer_class = serializers.LoginSerializer

    def login(self, request, format="json"):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class LoginOTP(GenericViewSet):

    authentication_classes = []
    serializer_class = serializers.OTPSerializer

    @transaction.atomic
    def generate(self, request, format=None):
        response = {'exists': 0}
        serializer = serializers.OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone_number = data['phone_number']

        otp_obj = data.get('otp_obj')

        req_type = request.query_params.get('type')
        via_sms = data.get('via_sms', True)
        via_whatsapp = data.get('via_whatsapp', False)
        call_source = data.get('request_source')
        retry_send = request.query_params.get('retry', False)
        # otp_message = OtpVerifications.get_otp_message(request.META.get('HTTP_PLATFORM'), req_type, version=request.META.get('HTTP_APP_VERSION'))
        otp_message = "test"
        send_otp(otp_message, phone_number, retry_send, via_sms=via_sms, via_whatsapp=via_whatsapp, call_source=call_source)
        if User.objects.filter(phone_number=phone_number, user_type=User.CONSUMER).exists():
            response['exists'] = 1

        return Response(response)

    def verify(self, request, format=None):

        # serializer = serializers.OTPVerificationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        return Response({"message": "OTP Generated Sucessfuly."})

class UploadDocument(GenericViewSet):

    def upload(self, request, format='json'):
        
        response = {
                "status": 0,
                "message": "File Uploaded successfully",
                "data": ""
        }
        data = request.data

        user_id = data.get("user_id")
        files = request.FILES

        try:
            docs = Documents.objects.add_attachments(files, user_id)
        except DocumentInvalid as e:
            response["status"] = 1
            response["message"] = str(e)
            return Response(response)

        user_docs = []
        for doc in docs:
            temp_data = {"doc": doc.pk, "user":user_id}
            user_doc_serializer = serializers.UserDocumentSerializer(data = temp_data)
            user_doc_serializer.is_valid(raise_exception=True)
            user_doc_serializer.save()
            user_docs.append(user_doc_serializer.data)
        response["data"] = user_docs
        return Response(response)







