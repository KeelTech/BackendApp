from datetime import date, timedelta
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
from rest_framework.views import APIView

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError

from keel.document.models import Documents
from keel.document.exceptions import DocumentInvalid, DocumentTypeInvalid
from keel.authentication.models import (CustomerProfile, CustomerProfileLabel, CustomerQualifications, CustomerWorkExperience, 
                                        UserDocument, QualificationLabel, WorkExperienceLabel, RelativeInCanadaLabel, RelativeInCanada,
                                        EducationalCreationalAssessment, EducationalCreationalAssessmentLabel)
from keel.api.v1.cases.serializers import CasesSerializer
from keel.cases.models import Case
from keel.authentication.models import (CustomToken, PasswordResetToken)
from keel.authentication.models import User as user_model
from keel.authentication.backends import JWTAuthentication
from keel.authentication.interface import get_rcic_item_counts
from keel.Core.constants import GENERIC_ERROR
from keel.Core.err_log import log_error
from keel.Core.notifications import EmailNotification
from keel.api.v1.auth import serializers
from keel.api.v1.document.serializers import DocumentCreateSerializer, DocumentTypeSerializer
from keel.api.permissions import IsRCICUser 

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from .adapter import GoogleOAuth2AdapterIdToken
from .auth_token import generate_auth_login_token
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
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # if user account is not active, send a email with token to activate user account
        # commenting this out for now
        current_time = str(datetime.datetime.now().timestamp()).split(".")[0]
        context = {
            'token' : current_time
        }
        subject = 'Account Verification'
        html_content = get_template('account_verification.html').render(context)
        # send email
        try:
            emails = EmailNotification(subject, html_content, [user.email])
            emails.send_email()
        except Exception as e:
                logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
                response['message'] = str(e)
                response['status'] = 0
                return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)

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
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
            # obj = generate_auth_login_token(user)
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
        except User.DoesNotExist as e:
            logger.error('ERROR: AUTHENTICATION:GeneratePasswordReset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:GeneratePasswordReset ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_501_NOT_IMPLEMENTED)
        
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
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
            # obj = generate_auth_login_token(user)
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
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
            # obj = generate_auth_login_token(user)
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


class ProfileView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class_pro = serializers.CustomerProfileSerializer
    serializer_class_profile = serializers.CustomerProfileLabelSerializer
    serializer_class_qualification = serializers.CustomerQualificationsLabelSerializer
    serializer_class_experience = serializers.WorkExperienceLabelSerializer
    serializer_class_relative_in_canada = serializers.RelativeInCanadaLabelSerializer
    serializer_class_education_assessment = serializers.EducationalCreationalAssessmentLabelSerializer
    serializer_class_cases = CasesSerializer

    def get_queryset_qualification(self, request):
        get_labels = QualificationLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['institute_label'] = label.institute_label
            labels['year_of_passing_label'] = label.year_of_passing_label
            labels['city_label'] = label.city_label
            labels['country_label'] = label.country_label
            labels['start_date_label'] = label.start_date_label
            labels['end_date_label'] = label.end_date_label
        queryset = CustomerQualifications.objects.filter(user=request.user)
        if queryset:
            serializer = self.serializer_class_qualification(queryset, many=True, context={"labels":labels})
            for label in serializer.data:
                label.pop("labels")
            return serializer.data
        else:
            data = {
                "institute": {"value": "", "type": "char", "labels": "Institute"},
                "year_of_passing": {"value": "", "type": "char", "labels": "Year Of Passing"},
                "city": {"value": "", "type": "char", "labels": "City"},
                "country": {"value": "", "type": "char", "labels": "Country"},
                "start_date": {"value": "", "type": "char", "labels": "Start Date"},
                "end_date": {"value": "", "type": "char", "labels": "End Date"}
            }
            return data
    
    def get_queryset_education_assessment(self, request):
        get_labels = EducationalCreationalAssessmentLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['eca_authority_name_label'] = label.eca_authority_name_label
            labels['eca_authority_number_label'] = label.eca_authority_number_label
            labels['canadian_equivalency_summary_label'] = label.canadian_equivalency_summary_label
        queryset = EducationalCreationalAssessment.objects.filter(user=request.user)
        if queryset:
            serializer = self.serializer_class_education_assessment(queryset, many=True, context={"labels":labels})
            return serializer.data
        else:
            data = {
                "eca_authority_name": {"value": "", "type": "char", "labels": "ECA Authority Name"},
                "eca_authority_number": {"value": "", "type": "char", "labels": "ECA Authority Number"},
                "canadian_equivalency_summary": {"value": "", "type": "char", "labels": "Canadian Equivalency Summary"},
            }
            return data
    
    def get_queryset_relative_in_canada(self, request):
        get_labels = RelativeInCanadaLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['full_name_label'] = label.full_name_label
            labels['relationship_label'] = label.relationship_label
            labels['immigrations_status_label'] = label.immigrations_status_label
            labels['address_label'] = label.address_label
            labels['contact_number_label'] = label.contact_number_label
            labels['email_address_label'] = label.email_address_label
        queryset = RelativeInCanada.objects.filter(user=request.user)
        if queryset:
            serializer = self.serializer_class_relative_in_canada(queryset, many=True, context={"labels":labels})
            return serializer.data
        else:
            data = {
                "full_name": {"value": "", "type": "char", "labels": "Full Name"},
                "relationship": {"value": "", "type": "char", "labels": "Relationship"},
                "immigration_status": {"value": "", "type": "char", "labels": "Immigration Status"},
                "address": {"value": "", "type": "char", "labels": "Address"},
                "contact_number": {"value": "", "type": "char", "labels": "Contact Number"},
                "email_address": {"value": "", "type": "char", "labels": "Email Address"}
            }
            return data
    
    def get_queryset_experience(self, request):
        get_labels = WorkExperienceLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['job_type_label'] = label.job_type_label
            labels['designation_label'] = label.designation_label
            labels['job_description_label'] = label.job_description_label
            labels['company_name_label'] = label.company_name_label
            labels['city_label'] = label.city_label
            labels['weekly_working_hours_label'] = label.weekly_working_hours_label
            labels['start_date_label'] = label.start_date_label
            labels['end_date_label'] = label.end_date_label
        queryset = CustomerWorkExperience.objects.filter(user=request.user)
        if queryset:
            serializer = self.serializer_class_experience(queryset, many=True, context={"labels":labels})
            for label in serializer.data:
                label.pop("labels")
            return serializer.data
        else:
            data = {
                "company_name": {"value": "", "type": "char", "labels": "Company Name"},
                "start_date": {"value": "", "type": "char", "labels": "Start Date"},
                "end_date": {"value": "", "type": "char", "labels": "End Date"},
                "city": {"value": "", "type": "char", "labels": "City"},
                "weekly_working_hours": {"value": "", "type": "char", "labels": "Weekly Working Hours"},
                "designation": {"value": "", "type": "char", "labels": "Desgination"},
                "job_type": {"value": "", "type": "char", "labels": "Job Type"},
                "job_description": {"value": "", "type": "char", "labels": "Job Description"}
            }
            return data

    def get_queryset_profile(self, request):
        get_labels = CustomerProfileLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['first_name_label'] = label.first_name_label
            labels['last_name_label'] = label.last_name_label
            labels['mother_fullname_label'] = label.mother_fullname_label
            labels['father_fullname_label'] = label.father_fullname_label
            labels['age_label'] = label.age_label
            labels['address_label'] = label.address_label
            labels['date_of_birth_label'] = label.date_of_birth_label
        profile = CustomerProfile.objects.filter(user=self.request.user.id)
        if profile:
            serializer = self.serializer_class_profile(profile, many=True, context={"labels":labels})
            for label in serializer.data:
                label.pop("labels")
            return serializer.data
        else:
            data = {
                "first_name": {"value": "", "type": "char", "labels": "First Name"},
                "last_name": {"value": "", "type": "char", "labels": "Last Name"},
                "mother_fullname": {"value": "", "type": "char", "labels": "Mother's Fullname"},
                "father_fullname": {"value": "", "type": "char", "labels": "Father's Fullname"},
                "age": {"value": "", "type": "char", "labels": "Age"},
                "address": {"value": "", "type": "char", "labels": "Address"},
                "date_of_birth": {"value": "", "type": "char", "labels": "Date of Birth"}
            }
            return data
    
    def get_queryset_cases(self, request):
        get_cases = Case.objects.filter(user=request.user).first()
        serializer = self.serializer_class_cases(get_cases)
        return serializer.data

    def create_profile(self, request):
        response = {
            "status" : 1,
            "message" : ""
        } 
        serializer = self.serializer_class_pro(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user'] = request.user
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:ProfileView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)
    
    def get_profile(self, request):
        response = {
            "status" : 1,
            "message" : ""
        } 
        queryset = CustomerProfile.objects.filter(user=request.user)
        serializer = self.serializer_class_pro(queryset, many=True)
        if serializer.data == []:
            response["message"] = {"profile_exists":False, "profile":serializer.data, "cases":self.get_queryset_cases(request)}
            return Response(response)

        response["message"] = {"profile_exists":True, "profile":serializer.data[0], "case":self.get_queryset_cases(request)}
        return Response(response)

    def get_full_profile(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }   
        profile = self.get_queryset_profile(request)
        qualification = self.get_queryset_qualification(request)
        work_experience = self.get_queryset_experience(request)
        relative_in_canada = self.get_queryset_relative_in_canada(request)
        education_assessment = self.get_queryset_education_assessment(request)
        cases = self.get_queryset_cases(request)
        response["message"] = {
                                "profile" : profile, 
                                "qualification" : qualification, 
                                "work_experience" : work_experience, 
                                "relative_in_canada" : relative_in_canada,
                                "education_assessment" : education_assessment,
                                "cases":cases
                            }
        return Response(response)


class QualificationView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.CustomerQualificationsSerializer

    def get_qualification(self, request, format="json"):
        queryset = CustomerQualifications.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "institute" : info["institute"].get("value"),
                "year_of_passing" : info["year_of_passing"].get("value"),
                "city" : info["city"].get("value"),
                "country" : info["country"].get("value"),
                "grade" : info["grade"].get("value"),
                "start_date" : info["start_date"].get("value"),
                "end_date" : info["end_date"].get("value"),
            }
            data.append(customer_work_info)
        return data

    def qualification(self, request):
        user = request.user
        response = {
            "status" : 1,
            "message" : ""
        }
        request = self.extract(request.data)
        serializer = self.serializer_class(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            data['user'] = user
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:CreateQualificationView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)


class WorkExperienceView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.CustomerWorkExperienceSerializer

    def get_work_experience(self, request, format="json"):
        queryset = CustomerWorkExperience.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "company_name" : info["company_name"].get("value"),
                "job_type" : info["job_type"].get("value"),
                "designation" : info["designation"].get("value"),
                "job_description" : info["job_description"].get("value"),
                "city" : info["city"].get("value"),
                "weekly_working_hours" : info["weekly_working_hours"].get("value"),
                "start_date" : info["start_date"].get("value"),
                "end_date" : info["end_date"].get("value")
            }
            data.append(customer_work_info)
        return data

    def work_exp(self, request):
        user = request.user
        response = {
            "status" : 1,
            "message" : ""
        }
        request = self.extract(request.data)
        serializer = self.serializer_class(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            data['user'] = user
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:CreateWorkExperienceView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)

class RelativeInCanadaView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.RelativeInCanadaSerializer

    def get_relative_in_canada(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        queryset = RelativeInCanada.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        response["message"] = serializer.data
        return Response(response)
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "full_name" : info["full_name"].get("value"),
                "relationship" : info["relationship"].get("value"),
                "immigration_status" : info["immigration_status"].get("value"),
                "address" : info["address"].get("value"),
                "contact_number" : info["contact_number"].get("value"),
                "email_address" : info["email_address"].get("value"),
            }
            data.append(customer_work_info)
        return data

    def relative_in_canada(self, request):
        user = request.user
        response = {
            "status" : 1,
            "message" : ""
        }
        request = self.extract(request.data)
        serializer = self.serializer_class(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            data['user'] = user
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:RelativeInCanadaView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)


class EducationalCreationalAssessmentView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.EducationalCreationalAssessmentSerializer

    def get_educational_creational_assessment(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        queryset = EducationalCreationalAssessment.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        response["message"] = serializer.data
        return Response(response)
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            print(info)
            customer_work_info = {
                "eca_authority_name" : info["eca_authority_name"].get("value"),
                "eca_authority_number" : info["eca_authority_number"].get("value"),
                "canadian_equivalency_summary" : info["canadian_equivalency_summary"].get("value"),
            }
            data.append(customer_work_info)
        return data

    def educational_creational_assessment(self, request):
        user = request.user
        response = {
            "status" : 1,
            "message" : ""
        }
        request = self.extract(request.data)
        serializer = self.serializer_class(data=request, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        for data in validated_data:
            data['user'] = user
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:EducationalCreationalAssessment ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)


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

        req_data = request.data

        user = request.user
        user_id = user.id
        files = request.FILES

        doc_type = req_data.get("doc_type")

        doc_serializer = DocumentCreateSerializer(data = request.FILES.dict())
        doc_serializer.is_valid(raise_exception=True)

        doc_type_serializer = DocumentTypeSerializer(data = {"doc_type": doc_type})
        doc_type_serializer.is_valid(raise_exception = True)

        try:
            docs = Documents.objects.add_attachments(files, user_id, doc_type)
        except (DocumentInvalid, DocumentTypeInvalid) as e:
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

        doc_user_id = user_id

        # Validate for Task Id, and replace the doc_user_id with task.user_id
        try:
            task_id = req_data.get("task_id")
            if task_id:
                task_serializer = serializers.TaskIDSerializer(data = {"task_id":task_id})
                task_serializer.is_valid(raise_exception = True)
                task_obj = task_serializer.validated_data
                doc_user_id = task_obj.user_id

        except ValidationError as e:
            log_error("ERROR","UploadDocument: upload taskValidation", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, status = resp_status)

        # validate and create User Doc
        try:
            user_docs = []
            for doc in docs:
                temp_data = {"doc": doc.pk, "user":doc_user_id, "task": task_id}
                user_doc_serializer = serializers.UserDocumentSerializer(data = temp_data)
                user_doc_serializer.is_valid(raise_exception=True)
                user_doc_serializer.save()
                user_docs.append(user_doc_serializer.data) 
            response["data"] = user_docs
        except ValidationError as e:
            log_error("ERROR","UploadDocument: upload", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
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
            user_docs = UserDocument.objects.select_related('doc','doc__doc_type'). \
                            filter(user_id = user.id, deleted_at__isnull = True)
            user_doc_serializer = serializers.ListUserDocumentSerializer(user_docs, many =True)
            response_data = user_doc_serializer.data
            response["data"] = response_data
        except Exception as e:
            log_error("ERROR", "UploadDocument:fetch exception", str(user.id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(response, status = resp_status)

    def deleteUserDoc(self, request, format = 'json', **kwargs):

        response = {
                "status": 0,
                "message": "User Document is deleted",
                "data": ""
        }

        resp_status = status.HTTP_200_OK
        user = request.user
        user_id = user.id
        user_doc_id = kwargs.get("id")

        try:
            user_doc = UserDocument.objects.select_related('doc').get(id = user_doc_id)
        except UserDocument.DoesNotExist as e:
            log_error("ERROR", "UploadDocument: deleteUserDoc ", str(user_id), err = "Invalid User Doc Id")
            response["status"] = 1
            response["message"] = "Invalid User Document Id"
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)
        except Exception as e:
            log_error("ERROR", "UploadDocument: deleteUserDoc ", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, status = resp_status)

        if user_doc.doc.owner_id != str(user_id):
            log_error("ERROR", "UploadDocument: deleteUserDoc ", str(user_id), err = "LoggedIn User is not a owner of document")
            response["status"] = 1
            response["message"] = "User is not authorised to perform this action"
            return Response(response, status = resp_status)
        try:        
            user_doc.mark_delete()
            user_doc.doc.mark_delete()
        except Exception as e:
            log_error("ERROR", "UploadDocument: deleteUserDoc mark_delete", str(user_id), err = str(e))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, status = resp_status)

        return Response(response, status = resp_status)


class ItemCount(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsRCICUser,)

    def getItemCount(self, request, format = 'json'):

        response = {
            "status": 0,
            "message": "Items counts successfully fetched",
            "data": ""
        }

        user = request.user

        resp_data, err_msg = get_rcic_item_counts(user)
        if err_msg:
            log_error("ERROR", "ItemCount:, ", str(user.id), err = str(err_msg))
            response["status"] = 1
            response["message"] = GENERIC_ERROR
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        response['data'] = resp_data
        return Response(response, status = status.HTTP_200_OK)

