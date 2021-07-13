from datetime import timedelta
import datetime
import facebook
import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction, IntegrityError, utils
from django.db.models import F, Sum, Max, Q, Prefetch, Case, When, Count, Value
from django.template.loader import get_template

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser

from keel.document.models import Documents
from keel.document.exceptions import *
from keel.authentication.models import UserDocument
from keel.authentication.backends import JWTAuthentication
from keel.Core.constants import GENERIC_ERROR
from keel.Core.err_log import log_error
from keel.Core.notifications import EmailNotification
from keel.api.v1.auth import serializers
from keel.authentication.models import (CustomToken, PasswordResetToken)
from keel.authentication.models import User as user_model
from .helpers.token_helper import save_token

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .adapter import GoogleOAuth2AdapterIdToken

# from keel.authentication.models import (OtpVerifications, )

import logging
logger = logging.getLogger('app-logger')

User = get_user_model()


class UserViewset(GenericViewSet):

    permission_classes = (AllowAny, )
    serializer_class = serializers.UserRegistrationSerializer

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def signup(self, request, format="json"):
        response = {
            'status' : 1,
            "message" : ''
        } 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user_type'] = user_model.CUSTOMER # add user type to validated data
        
        try:
            user = self.create(validated_data)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            token = JWTAuthentication.generate_token(user)
            token_to_save = save_token(token)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # # if user account is not active, send a email with token to activate user account
        # # commenting this out for now
        # current_time = str(datetime.datetime.now().timestamp()).split(".")[0]
        # context = {
        #     'token' : current_time
        # }
        # subject = 'Password Reset'
        # html_content = get_template('password_reset_email.html').render(context)
        # # send email
        # try:
        #     emails = EmailNotification(subject, html_content, [user.email])
        #     emails.send_email()
        # except Exception as e:
        #         logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
        #         response['message'] = str(e)
        #         response['status'] = 0
        #         return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "email" : obj.user.email,
            "token" : obj.token,
        }
        response["message"] = data
        return Response(response, status=status.HTTP_200_OK)
    
    def verify_account(self, request):
        pass

class LoginViewset(GenericViewSet):
    serializer_class = serializers.LoginSerializer

    def login(self, request, format="json"):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        # if not user.is_verified:
        #     response["status"] = 0
        #     response["message"] = "Acount has not been verified, Please check your email for verification code"
        #     return Response(response)
        
        try:
            token = JWTAuthentication.generate_token(user)
            token_to_save = save_token(token)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:LoginViewset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = {
            "email" : obj.user.email,
            "token" : obj.token,
        }
        response["message"] = data
        return Response(response, status=status.HTTP_200_OK)

class GeneratePasswordReset(GenericViewSet):
    serializer_class = serializers.GenerateTokenSerializer
    
    def token(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        current_time = str(datetime.datetime.now().timestamp()).split(".")[0]
        
        try:
            user = User.objects.get(email=email)
            expiry_date = timezone.now() + timedelta(minutes=10)
            obj, created = PasswordResetToken.objects.get_or_create(user=user, reset_token=current_time, expiry_date=expiry_date)
            context = {
                'token' : current_time
            }
            subject = 'Password Reset'
            html_content = get_template('password_reset_email.html').render(context)
            # send email
            emails = EmailNotification(subject, html_content, [email])
            emails.send_email()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:GeneratePasswordReset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        response["message"] = "Password Reset Link sent successfully"
        return Response(response)


class ConfirmPasswordReset(GenericViewSet):
    serializer_class = serializers.ConfirmResetTokenSerializer

    def confirm_reset(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        reset_token = validated_data.get('reset_token', None)
        password = validated_data['password']
        try:
            token = PasswordResetToken.objects.get(reset_token=reset_token)
            
            expiry_time = token.expiry_date
            time_now = timezone.now() + timedelta(minutes=0)
            if (expiry_time - time_now).total_seconds() < 0:
                token.delete() # delete token if expired
                response['status'] = 0
                response["message"] = "Reset token expired"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
           
            # get user and set password
            user = User.objects.get(email=token.user)
            user.set_password(password)
            user.save()
        except (PasswordResetToken.DoesNotExist, User.DoesNotExist) as e:
            logger.error('ERROR: AUTHENTICATION:ConfirmPasswordReset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:ConfirmPasswordReset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        # delete token since it has beeen used
        token.delete()

        response["message"] = "User password reset successful"
        return Response(response)


class ChangePasswordView(GenericViewSet):

    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def change_password_without_email(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        user = request.user
        old_password = validated_data.get('old_password', None)
        new_password1 = validated_data.get('new_password1', None)
        new_password2 = validated_data.get('new_password2', None)

        if not user.check_password(old_password):
            response['status'] = 0
            response["message"] = "Incorrect Password"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                response['status'] = 0
                response["message"] = "Password Mismatch"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password2)
            user.save()
        
        response["message"] = "User password changed successfully"
        return Response(response)

class FacebookLogin(GenericViewSet):
    serializer_class = serializers.FacebookSocialLoginSerializer

    @staticmethod
    def facebook(auth_token):
        response = {
            "status" : 1,
            "message" : ""
        }
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.get_object(id='me', fields='first_name, last_name, id, email')
            return profile
        except requests.ConnectionError as e:
            raise e
        except facebook.GraphAPIError as e:
            return e

    def fblogin(self, request, *args, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        validated_data = self.serializer.validated_data
        try:
            fb = self.facebook(validated_data['access_token'])
            email = fb['email']
            user, created = User.objects.get_or_create(email=email)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            token = JWTAuthentication.generate_token(user)
            token_to_save = save_token(token)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:FacebookLogin ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            "email" : obj.user.email,
            "token" : obj.token,
        }
        response["message"] =  data
        return Response(response)

class LinkedinLogin(SocialLoginView):
    adapter_class = LinkedInOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://localhost:8000/accounts/linkedin_oauth2/login/callback/"
    serializer_class = serializers.UserSocialLoginSerializer

    def post(self, request, *args, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        response["message"] =  self.serializer.data
        return Response(response)

    
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterIdToken
    client_class = OAuth2Client
    serializer_class = serializers.UserSocialLoginSerializer

    def post(self, request, *args, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        user = self.serializer.validated_data
        try:
            token = JWTAuthentication.generate_token(user)
            token_to_save = save_token(token)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:GoogleLogin ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            "email" : obj.user.email,
            "token" : obj.token,
        }
        response["message"] =  data
        return Response(response)

class UserDeleteTokenView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def remove(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        token = request.headers.get('Authorization', None).split(" ")[1]

        try:
            CustomToken.objects.get(token=token).delete()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:UserDeleteTokenView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        response["message"] = "User logged out successfully"
        return Response(response, status=status.HTTP_200_OK)

    
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

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)
    
    def upload(self, request, format='json'):
        response = {
                "status": 0,
                "message": "File Uploaded successfully",
                "data": ""
        }
        resp_status = status.HTTP_200_OK

        data = request.data

        user = request.user
        user_id = user.id
        files = request.FILES

        try:
            docs = Documents.objects.add_attachments(files, user_id)
        except DocumentInvalid as e:
            log_error("ERROR", "UploadDocument:upload DocumentInvalid", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = str(e)
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)
        except Exception as e:
            log_error("ERROR", "UploadDocument:upload Exception", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, status = resp_status)

        user_docs = []
        for doc in docs:
            temp_data = {"doc": doc.pk, "user":user_id}
            user_doc_serializer = serializers.UserDocumentSerializer(data = temp_data)
            user_doc_serializer.is_valid(raise_exception=True)
            user_doc_serializer.save()
            user_docs.append(user_doc_serializer.data) 
        response["data"] = user_docs
        return Response(response, status = resp_status)

    def fetch(self, request, format = 'json'):

        response = {
                "status": 0,
                "message":"User Document Fetched successfully",
                "data": ""
        }
        resp_status = status.HTTP_200_OK
        user = request.user

        try:
            user_docs = UserDocument.objects.select_related('doc').filter(user_id = user.id)
            user_doc_serializer = serializers.ListUserDocumentSerializer(user_docs, many =True)
            response_data = user_doc_serializer.data
            response["data"] = response_data
        except Exception as e:
            log_error("ERROR", "UploadDocument:fetch exception", str(user.id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status = resp_status)


