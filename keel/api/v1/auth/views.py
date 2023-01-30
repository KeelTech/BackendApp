import datetime
import json
import logging
from datetime import date, timedelta
from django.conf import settings

import facebook
import requests
from allauth.socialaccount.providers.facebook.views import \
    FacebookOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import \
    LinkedInOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction, utils
from django.template.loader import get_template
from django.utils import timezone
from keel.api.permissions import IsRCICUser
from keel.api.v1.auth import serializers
from keel.api.v1.cases.serializers import CasesSerializer
from keel.api.v1.document.serializers import (DocumentCreateSerializer,
                                              DocumentTypeSerializer)
from keel.api.v1.plans.serializers import PlanSerializers
from keel.authentication import constants
from keel.authentication.backends import JWTAuthentication
from keel.authentication.interface import get_rcic_item_counts
from keel.authentication.models import (AgentProfile, CustomerProfile,
                                        CustomerProfileLabel,
                                        CustomerQualifications,
                                        CustomerWorkExperience, CustomToken,
                                        EducationalCreationalAssessment,
                                        EducationalCreationalAssessmentLabel, CustomerFamilyInformationLabel,
                                        PasswordResetToken, QualificationLabel, CustomerFamilyInformation,
                                        RelativeInCanada, CustomerSpouseProfile, CustomerSpouseProfileLabel,
                                        RelativeInCanadaLabel, CustomerLanguageScoreLabel, CustomerLanguageScore)
from keel.authentication.models import User as user_model
from keel.authentication.models import UserDocument, WorkExperienceLabel
from keel.cases.models import Case
from keel.Core import constants as core_constants
from keel.Core.err_log import log_error, logging_format
from keel.Core.notifications import EmailNotification, SMSNotification
from keel.document.exceptions import DocumentInvalid, DocumentTypeInvalid
from keel.document.models import Documents
from keel.notifications.constants import DOCUMENT
from keel.notifications.models import InAppNotification
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .adapter import GoogleOAuth2AdapterIdToken
from .helpers.otp_helpers import OTPHelper


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

        # try:
        #     # send welcome email
        #     email_helper.send_welcome_email(user)
        
        # except Exception as e:
        #     logger.error('ERROR: AUTHENTICATION:UserViewset ' + str(e))
        #     pass

        data = {
            "email" : obj.user.email,
            "token" : obj.token,
        }
        response["message"] = data
        return Response(response, status=status.HTTP_200_OK)
    
    def verify_account(self, request):
        pass


class LoginViewset(GenericViewSet):
    serializer_class_customer = serializers.CustomerLoginSerializer
    serializer_class_agent = serializers.AgentLoginSerializer

    @staticmethod
    def login(serializer_class, request):
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return user

    def customer_login(self, request, format="json"):
        response = {
            "status" : 1,
            "message" : ""
        }
        user = self.login(self.serializer_class_customer, request)
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

    def agent_login(self, request, format="json"):
        response = {
            "status" : 1,
            "message" : ""
        }
        user = self.login(self.serializer_class_agent, request)
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
    serializer_class_pro_base = serializers.BaseProfileSerializer
    serializer_class_pro = serializers.CustomerProfileSerializer
    serializer_class_profile = serializers.CustomerProfileLabelSerializer
    serializer_class_spouse_profile = serializers.CustomerSpouseProfileLabelSerializer
    serializer_class_qualification = serializers.CustomerQualificationsLabelSerializer
    serializer_class_experience = serializers.WorkExperienceLabelSerializer
    serializer_class_relative_in_canada = serializers.RelativeInCanadaLabelSerializer
    serializer_class_education_assessment = serializers.EducationalCreationalAssessmentLabelSerializer
    serializer_class_cases = CasesSerializer
    serializer_class_language_scores = serializers.LanguageScoreLabelSerializer
    serializer_class_family_info = serializers.CustomerFamilyInfoLabelSerializer

    def get_queryset_qualification(self, request, profile_owner):
        get_labels = QualificationLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['institute_label'] = label.institute_label
            labels['degree_label'] = label.degree_label
            labels['year_of_passing_label'] = label.year_of_passing_label
            labels['grade_label'] = label.grade_label
            labels['city_label'] = label.city_label
            labels['state_label'] = label.state_label
            labels['country_label'] = label.country_label
            labels['start_date_label'] = label.start_date_label
            labels['end_date_label'] = label.end_date_label
        queryset = CustomerQualifications.objects.filter(user=request.user, owner=profile_owner)
        if queryset:
            serializer = self.serializer_class_qualification(queryset, many=True, context={"labels": labels,
                                                                                           "owner": profile_owner})
            for label in serializer.data:
                label.pop("labels")
            return serializer.data
        else:
            data = constants.QUALIFICATION
            data[0]['owner']['value'] = profile_owner
            return data
    
    def get_queryset_education_assessment(self, request, profile_owner):
        get_labels = EducationalCreationalAssessmentLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['eca_authority_name_label'] = label.eca_authority_name_label
            labels['eca_authority_number_label'] = label.eca_authority_number_label
            labels['canadian_equivalency_summary_label'] = label.canadian_equivalency_summary_label
            labels['eca_date_label'] = label.eca_date_label
        queryset = EducationalCreationalAssessment.objects.filter(user=request.user, owner=profile_owner)
        if queryset:
            serializer = self.serializer_class_education_assessment(queryset, many=True, context={"labels": labels,
                                                                                                  "owner": profile_owner})
            return serializer.data
        else:
            data = constants.ECA
            data[0]['owner']['value'] = profile_owner
            return data
    
    def get_queryset_relative_in_canada(self, request, profile_owner):
        get_labels = RelativeInCanadaLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['full_name_label'] = label.full_name_label
            labels['relationship_label'] = label.relationship_label
            labels['immigration_status_label'] = label.immigration_status_label
            labels['address_label'] = label.address_label
            labels['contact_number_label'] = label.contact_number_label
            labels['email_address_label'] = label.email_address_label
            labels['is_blood_relationship_label'] = label.is_blood_relationship_label
        queryset = RelativeInCanada.objects.filter(user=request.user, owner=profile_owner).first()
        if queryset:
            serializer = self.serializer_class_relative_in_canada(queryset, context={"labels": labels,
                                                                                     "owner": profile_owner})
            return serializer.data
        else:
            data = constants.RELATIVE
            data['owner']['value'] = profile_owner
            return data
    
    def get_queryset_experience(self, request, profile_owner):
        get_labels = WorkExperienceLabel.objects.filter(user_label="user")
        labels = {}
        for label in get_labels:
            labels['job_type_label'] = label.job_type_label
            labels['designation_label'] = label.designation_label
            labels['job_description_label'] = label.job_description_label
            labels['company_name_label'] = label.company_name_label
            labels['city_label'] = label.city_label
            labels['state_label'] = label.state_label
            labels['country_label'] = label.country_label
            labels['weekly_working_hours_label'] = label.weekly_working_hours_label
            labels['start_date_label'] = label.start_date_label
            labels['end_date_label'] = label.end_date_label
            labels['is_current_job_label'] = label.is_current_job_label
        queryset = CustomerWorkExperience.objects.filter(user=request.user, owner=profile_owner)
        if len(queryset):
            serializer = self.serializer_class_experience(queryset, many=True, context={"labels": labels,
                                                                                        "owner": profile_owner})
            for label in serializer.data:
                label.pop("labels")
            return serializer.data
        else:
            data = constants.WORK_EXPERIENCE
            data[0]['owner']['value'] = profile_owner
            return data

    def get_queryset_language_scores(self, request, profile_owner):
        labels_queryset = CustomerLanguageScoreLabel.objects.filter(user_label="user").values()
        if len(labels_queryset):
            labels = labels_queryset[0]

        queryset = CustomerLanguageScore.objects.filter(user=request.user, owner=profile_owner)
        if len(queryset):
            serializer = self.serializer_class_language_scores(queryset, many=True,  context={"labels": labels,
                                                                                              "owner": profile_owner})
            return serializer.data
        else:
            data = constants.LANGUAGESCORE
            data[0]['owner']['value'] = profile_owner
            return data

    def get_queryset_family_info(self, request):
        labels_queryset = CustomerFamilyInformationLabel.objects.filter(user_label="user").values()
        if len(labels_queryset):
            labels = labels_queryset[0]

        queryset = CustomerFamilyInformation.objects.filter(customer__user=request.user)
        if len(queryset):
            serializer = self.serializer_class_family_info(queryset, many=True, context={"labels": labels})
            return serializer.data
        else:
            data = constants.CUSTOMERFAMILYINFO
            return data

    def get_queryset_profile(self, request):
        labels_queryset = CustomerProfileLabel.objects.filter(user_label="user").values()
        if len(labels_queryset):
            labels = labels_queryset[0]

        profile = CustomerProfile.objects.filter(user=self.request.user.id).first()
        if profile:
            serializer = self.serializer_class_profile(profile, context={"labels": labels})
            # serializer.data.pop("labels")
            return serializer.data
        else:
            data = constants.PROFILE
            return data

    def get_queryset_spouse_profile(self, request):
        labels_queryset = CustomerSpouseProfileLabel.objects.filter(user_label="user").values()
        if len(labels_queryset):
            labels = labels_queryset[0]

        profile = CustomerSpouseProfile.objects.filter(customer__user=self.request.user).first()
        if profile:
            serializer = self.serializer_class_spouse_profile(profile, context={"labels": labels})
            return serializer.data
        else:
            data = constants.SPOUSEPROFILE
            return data
    
    def get_queryset_cases(self, user):
        get_case = None
        try:
            get_case = Case.objects.select_related('plan').get(user=user, is_active=True)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:GetCases ' + str(e))
        plan = ""
        if get_case is not None:
            plan = PlanSerializers(get_case.plan).data['plan_type']
        serializer = self.serializer_class_cases(get_case).data
        agent = serializer['agent']
        get_agent = AgentProfile.objects.filter(agent=agent).first()
        agent = serializers.AgentProfileSerializer(get_agent).data
        return {"case_details":serializer, "agent":agent, "plan_type":plan}

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

    def create_initial_profile(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        serializer = serializers.InitialProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        phone_number = validated_data['phone_number']
        validated_data['user'] = request.user
        try:
            validated_data.pop('phone_number')
            serializer.save()
            get_user = User.objects.get(id=request.user.id)
            get_user.phone_number = phone_number
            get_user.save()
        except IntegrityError as e:
            logger.error('ERROR: AUTHENTICATION:ProfileView ' + str(e))
            response['message'] = "User already has a profile"
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:ProfileView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response["message"] = serializer.data
        return Response(response)

    def update_full_profile(self, request):
        response = {
            "status": 0,
            "message": ""
        }
        exception = 0

        profile_components = {'profile': CustomerInformationView,
                              'qualification': QualificationView,
                              'work_experience': WorkExperienceView,
                              'relative_in_canada': RelativeInCanadaView,
                              'education_assessment': EducationalCreationalAssessmentView,
                              'language_scores': LanguageScoreView,
                              'spouse_profile': SpouseProfileView,
                              'family_information': FamilyInformationView
                              }

        component_req = list(request.data.keys())[0]
        if component_req not in profile_components:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                error, msg = profile_components[component_req].update(request.data[component_req], request.user)
                if error:
                    exception = 1
                    response['message'] = msg
        except Exception as e:
            response['message'] = str(e)
            exception = 1

        if exception:
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response["status"] = 1
        return Response(response)
    
    def get_profile(self, request):
        user = request.user
        case = self.get_queryset_cases(user)
        response = {
            "status" : 1,
            "message" : {"profile_exists": False,  "profile":{}, "cases":case["case_details"], "agent":case["agent"]}
        } 
        queryset = CustomerProfile.objects.filter(user=request.user).first()
        if not queryset:
            return Response(response)

        serializer = self.serializer_class_pro_base(queryset)
        response["message"]["profile_exists"] = True
        response["message"]["profile"] = serializer.data
        response["message"]["plan_type"] = case.get('plan_type')

        return Response(response)

    def get_full_profile(self, request):
        response = {
            "status": 1,
            "message": {}
        }

        self_data = {
            "profile": self.get_queryset_profile(request),
            "qualification": self.get_queryset_qualification(request, core_constants.SELF),
            "work_experience": self.get_queryset_experience(request, core_constants.SELF),
            "relative_in_canada": self.get_queryset_relative_in_canada(request, core_constants.SELF),
            "education_assessment": self.get_queryset_education_assessment(request, core_constants.SELF),
            "language_scores": self.get_queryset_language_scores(request, core_constants.SELF),
            "family_information": self.get_queryset_family_info(request),
        }

        spouse_data = {
            'profile': self.get_queryset_spouse_profile(request),
            'qualification': self.get_queryset_qualification(request, core_constants.SPOUSE),
            'work_experience': self.get_queryset_experience(request, core_constants.SPOUSE),
            'relative_in_canada': self.get_queryset_relative_in_canada(request, core_constants.SPOUSE),
            'education_assessment': self.get_queryset_education_assessment(request, core_constants.SPOUSE),
            'language_scores': self.get_queryset_language_scores(request, core_constants.SPOUSE),
        }
        response["message"]['self'] = self_data
        response["message"]['spouse'] = spouse_data

        return Response(response)


class QualificationView(GenericViewSet):
    serializer_class = serializers.CustomerQualificationsSerializer
    serializer_class_update = serializers.CustomerQualificationUpdateSerializer

    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "id": info.get("id"),
                "institute": info["institute"].get("value"),
                "degree": info["degree"].get("value"),
                "year_of_passing": info["year_of_passing"].get("value"),
                "city": info["full_address"].get("cityId"),
                "state": info["full_address"].get("stateId"),
                "country": info["full_address"].get("countryId"),
                "grade": info["grade"].get("value"),
                "start_date": info["start_date"].get("value"),
                "end_date": info["end_date"].get("value"),
                "owner": info.get("owner"),
            }
            data.append(customer_work_info)
        return data

    @staticmethod 
    def create(validated_data):
        id = validated_data.get('id')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        if start_date is not None and end_date is not None and end_date < start_date:
            raise serializers.ValidationError("Start Date cannot be greater then end date")
        
        try:
            CustomerQualifications.objects.update_or_create(id=id, defaults={
                                                    "institute": validated_data.get('institute'),
                                                    "degree": validated_data.get('degree'),
                                                    "grade": validated_data.get('grade'),
                                                    "year_of_passing": validated_data.get('year_of_passing'),
                                                    "start_date": validated_data.get('start_date'),
                                                    "end_date": validated_data.get('end_date'),
                                                    "city": validated_data.get('city'),
                                                    "state": validated_data.get('state'),
                                                    "country": validated_data.get('country'),
                                                    "user": validated_data.get('user'),
                                                    "owner": validated_data.get('owner'),
                                                })
        except Exception as err:
            logger.error(str(err))
            return True, str(err)
        return False, ''

    @classmethod
    def update(cls, data, user):

        # CustomerQualifications.objects.filter(user=user).delete()
        obj_data = cls.extract(data)
        serializer = cls.serializer_class_update(data=obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        enum_validated_data = dict(enumerate(validated_data))
        count = 0
        for ids in obj_data:
            validated_data_from_dict = enum_validated_data[count]
            validated_data_from_dict['id'] = ids.get('id')
            validated_data_from_dict['user'] = user
            error, msg = cls.create(validated_data_from_dict)
            if error:
                return error, msg
            count += 1
        return error, msg


class WorkExperienceView(GenericViewSet):
    serializer_class = serializers.CustomerWorkExperienceSerializer
    serializer_class_update = serializers.CustomerUpdateWorkExperienceSerializer
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "id": info.get("id"),
                "company_name": info["company_name"].get("value"),
                "job_type": info["job_type"].get("value"),
                "designation": info["designation"].get("value"),
                "job_description": info["job_description"].get("value"),
                "city": info["full_address"].get("cityId"),
                "state": info["full_address"].get("stateId"),
                "country": info["full_address"].get("countryId"),
                "weekly_working_hours": info["weekly_working_hours"].get("value"),
                "start_date": info["start_date"].get("value"),
                "end_date": info["end_date"].get("value"),
                "is_current_job": info["is_current_job"].get("value"),
                "owner": info.get('owner').get('value'),
            }
            if customer_work_info['end_date'] == '':
                del customer_work_info['end_date']
            data.append(customer_work_info)
        return data
    
    @staticmethod
    def create(validated_data):
        id = validated_data.get('id')
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        
        # validate date
        if end_date is not None and start_date is not None and end_date < start_date:
            raise serializers.ValidationError("Start Date cannot be greater then end date")
        
        try:
            CustomerWorkExperience.objects.update_or_create(id=id,
                                defaults={
                                    "job_type": validated_data.get('job_type'),
                                    "designation": validated_data.get('designation'),
                                    "company_name": validated_data.get('company_name'),
                                    "job_description": validated_data.get('job_description'),
                                    "city": validated_data.get('city'),
                                    "state": validated_data.get('state'),
                                    "country": validated_data.get('country'),
                                    "weekly_working_hours": validated_data.get('weekly_working_hours'),
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "is_current_job": validated_data.get('is_current_job'),
                                    "user": validated_data.get('user'),
                                    "owner": validated_data.get('owner'),
                                })
        except Exception as err:
            logger.error(str(err))
            return True, str(err)
        return False, ''

    @classmethod
    def update(cls, data, user):
        # CustomerWorkExperience.objects.filter(user=user).delete()
        obj_data = cls.extract(data)
        serializer = cls.serializer_class_update(data=obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        enum_validated_data = dict(enumerate(validated_data))
        count = 0
        for ids in obj_data:
            validated_data_from_dict = enum_validated_data[count]
            validated_data_from_dict['id'] = ids.get('id')
            validated_data_from_dict['user'] = user
            error, msg = cls.create(validated_data_from_dict)
            if error:
                return error, msg
            count += 1
        return error, msg


class RelativeInCanadaView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.RelativeInCanadaSerializer
    serializer_class_update = serializers.RelativeInCanadaUpdateSerializer

    @staticmethod
    def extract(datas):
        relative_info = {
            "id": datas.get("id"),
            "full_name": datas["full_name"].get("value"),
            "relationship": datas["relationship"].get("value"),
            "immigration_status": datas["immigration_status"].get("value"),
            "address": datas["address"].get("value"),
            "contact_number": datas["contact_number"].get("value"),
            "email_address": datas["email_address"].get("value"),
            "is_blood_relationship": datas["is_blood_relationship"].get("value"),
            "owner": datas.get('owner').get('value'),
        }
        return relative_info

    @classmethod
    def update(cls, data, user):
        obj_data = cls.extract(data)
        id = obj_data.get('id')
        serializer = cls.serializer_class_update(data=obj_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user'] = user
        validated_data['id'] = id
        try:
            serializer.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:RelativeInCanadaView ' + str(e))
            return True, str(e)
        return False, ''


class EducationalCreationalAssessmentView(GenericViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = serializers.EducationalCreationalAssessmentSerializer
    serializer_class_update = serializers.EducationalCreationalAssessmentUpdateSerializer
    
    @staticmethod
    def extract(datas):
        data = []
        for info in datas:
            customer_work_info = {
                "id": info.get("id"),
                "eca_authority_name": info["eca_authority_name"].get("value"),
                "eca_authority_number": info["eca_authority_number"].get("value"),
                "canadian_equivalency_summary": info["canadian_equivalency_summary"].get("value"),
                "eca_date": info["eca_date"].get("value"),
                "owner": info.get('owner').get('value'),
            }
            data.append(customer_work_info)
        return data
    
    @staticmethod
    def create(validated_data):
        try:
            EducationalCreationalAssessment.objects.update_or_create(id=validated_data.get('id'),
                                defaults={
                                        "eca_authority_name": validated_data.get('eca_authority_name'),
                                        "eca_authority_number": validated_data.get('eca_authority_number'),
                                        "canadian_equivalency_summary": validated_data.get('canadian_equivalency_summary'),
                                        "eca_date": validated_data.get("eca_date"),
                                        "user": validated_data.get('user'),
                                        "owner": validated_data.get('owner'),
                                    })
        except Exception as err:
            logger.error(str(err))
            return True, str(err)
        return False, ''

    @classmethod
    def update(cls, data, user):
        # EducationalCreationalAssessment.objects.filter(user=user).delete()
        obj_data = cls.extract(data)
        serializer = cls.serializer_class_update(data=obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        enum_validated_data = dict(enumerate(validated_data))
        count = 0
        for ids in obj_data:
            validated_data_from_dict = enum_validated_data[count]
            validated_data_from_dict['id'] = ids.get('id')
            validated_data_from_dict['user'] = user
            error, msg = cls.create(validated_data_from_dict)
            if error:
                return error, msg
            count += 1
        return error, msg


class LoginOTP(GenericViewSet):

    @transaction.atomic
    def generate(self, request):

        response = {
            "status": "0",
            "data": ""
        }
        serializer = serializers.OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone_number = data['phone_number']

        token = "MOBILE_VERIFICATION_"

        # create otp
        otp_instance = OTPHelper(phone_number)
        otp = otp_instance.save_otp(phone_number)
        text = "{0} is the OTP for mobile verification".format(otp)
        sms = SMSNotification(phone_number, text)
        err = sms.send_sms()
        if err:
            log_error("CRITICAL", "LoginOTP.generate", "Failed to send SMS", err=str(err))
            response["data"] = str(err)
        else:
            response["data"] = {"token": token}
            response["status"] = 1

        return Response(response)

    def verify(self, request):

        # serializer = serializers.OTPVerificationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        response = {
            "status": "0",
            "data": "",
        }

        req_data = request.data
        user = request.user

        otp_verify = serializers.VerifyOTPSerializer(data=req_data)
        otp_verify.is_valid(raise_exception=True)
        data = otp_verify.validated_data
        otp = data['otp']
        phone = data['phone_number']

        # otp instance
        otp_instance = OTPHelper(phone)
        otp_verify = otp_instance.verify_otp(otp)

        if not otp_verify:
            log_error("ERROR", "LoginOTP.verify", "OTP is invalid")
            response["data"] = "OTP is invalid"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        phone_number = otp_verify.get("phone_number")

        if not user.is_anonymous:
            user.phone_number = phone_number
            user.save()
        otp_instance.delete_otp()
        response['status'] = 1
        response["data"] = "OTP validated successfully"
        return Response(response, status=status.HTTP_200_OK)


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

        case_id = req_data.get("case","")

        # Catching the case Id exception unless FE start passing it, TODO: Remove it once done
        try:
            from keel.api.v1.cases.serializers import CaseIDSerializer

            # validate Case ID against User/Agent
            case_serializer = CaseIDSerializer(data = {"case_id": case_id, "user_id": user_id})
            case_serializer.is_valid(raise_exception=True)
            case_obj = case_serializer.validated_data
            
            # actual user containing the document
            doc_user_id = case_obj.user_id

        except:
            doc_user_id = user_id
            pass
        
        doc_type = req_data.get("doc_type")
        doc_serializer = DocumentCreateSerializer(data = request.FILES.dict())
        doc_serializer.is_valid(raise_exception=True)

        doc_type_serializer = DocumentTypeSerializer(data = {"doc_type": doc_type})
        doc_type_serializer.is_valid(raise_exception = True)

        try:
            docs = Documents.objects.add_attachments(files, user_id, doc_type)
        except (DocumentInvalid, DocumentTypeInvalid) as e:
            log_error("ERROR", "UploadDocument:upload DocumentInvalid", str(user_id), err=str(e))
            response["status"] = 1
            response["message"] = str(e)
            resp_status = status.HTTP_400_BAD_REQUEST
            return Response(response, status = resp_status)
        except Exception as e:
            log_error("ERROR", "UploadDocument:upload Exception", str(user_id), err=str(e))
            response["status"] = 1
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(response, status = resp_status)

        # Validate for Task Id, and replace the doc_user_id with task.user_id
        try:
            task_id = req_data.get("task_id")
            if task_id:
                task_serializer = serializers.TaskIDSerializer(data={"task_id": task_id})
                task_serializer.is_valid(raise_exception=True)
                task_obj = task_serializer.validated_data
                doc_user_id = task_obj.user_id

        except ValidationError as e:
            log_error("ERROR","UploadDocument: upload taskValidation", str(user_id), err=str(e))
            response["status"] = 1
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
            log_error("ERROR","UploadDocument: upload", str(user_id), err=str(e))
            response["status"] = 1
            resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # create a notification instance
        case_id_notification = request.user.users_cases.first()
        notification = InAppNotification.objects.create(
            text = "New Document uploaded",
            user_id = user, 
            case_id = case_id_notification, 
            category = DOCUMENT
        )

        return Response(response, status = resp_status)

    # works for both User and agent based on case id
    def fetch(self, request, format = 'json'):

        response = {
                "status": 0,
                "message":"User Document Fetched successfully",
                "data": ""
        }
        resp_status = status.HTTP_200_OK
        user = request.user
        user_id = user.id

        req_data = request.GET.dict()
        case_id = req_data.get("case","")

        # Catching the case Id exception unless FE start passing it, TODO: Remove it once done
        try:
            from keel.api.v1.cases.serializers import CaseIDSerializer

            # validate Case ID against User/Agent
            case_serializer = CaseIDSerializer(data = {"case_id": case_id, "user_id": user_id})
            case_serializer.is_valid(raise_exception=True)
            case_obj = case_serializer.validated_data
            
            # actual user containing the document
            actual_user_id = case_obj.user_id
        except:
            actual_user_id = user_id
            pass

        try:
            user_docs = UserDocument.objects.select_related('doc','doc__doc_type'). \
                            filter(user_id = actual_user_id, deleted_at__isnull = True).order_by("-updated_at")
            user_doc_serializer = serializers.ListUserDocumentSerializer(user_docs, many =True)
            response_data = user_doc_serializer.data
            response["data"] = response_data
        except Exception as e:
            log_error("ERROR", "UploadDocument:fetch exception", str(user.id), err = str(e))
            response["status"] = 1
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
            response["message"] = st(e)
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
            log_error("ERROR", "ItemCount:, ", str(user.id), err=str(err_msg))
            response["status"] = 1
            return Response(response, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

        response['data'] = resp_data
        return Response(response, status = status.HTTP_200_OK)


class AgentView(GenericViewSet):
    serializer_class = serializers.AgentProfileSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsRCICUser, )

    def agent_profile(self, request):
        user = request.user
        response = {
            "status" : 1,
            "message" : ""
        }
        try:
            queryset = AgentProfile.objects.select_related('agent').get(agent=user)
        except AgentProfile.DoesNotExist as e:
            logger.error('ERROR: AUTHENTICATION:AgentView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:AgentView ' + str(e))
            response['message'] = str(e)
            response['status'] = 0
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = serializers.AgentProfileSerializer(queryset).data
        user_serializer = serializers.UserSerializer(user).data
        response["message"] = {"agent_details" : user_serializer, "agent_profile" : serializer}
        return Response(response)
        

class NewUserFromGetRequest(GenericViewSet):

    def new_user(self, request):
        response = {"status": 0, "message": "", "data": ""}
        email = request.query_params.get('email', None)

        # check if email already exists
        check_email = User.objects.filter(email=email).first()

        if check_email:
            user = check_email
        else:
            DEFAULT_PASSWORD = settings.DEFAULT_USER_PASS
            user = User.objects.create_user(email=email, password=DEFAULT_PASSWORD)
        
        try:
            token_to_save = JWTAuthentication.generate_token(user)
            obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
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


class LanguageScoreView(GenericViewSet):

    @classmethod
    def extract_lang_data(cls, data):
        out = []
        for info in data:
            customer_lang_score = {
                "id": info.get("id"),
                "test_type": info["test_type"].get("value"),
                "test_date": info["test_date"].get("value"),
                "result_date": info["result_date"].get("value"),
                "listening_score": info["listening_score"].get("value"),
                "test_version": info["test_version"].get("value"),
                "report_form_number": info["report_form_number"].get("value"),
                "writing_score": info["writing_score"].get("value"),
                "speaking_score": info["speaking_score"].get("value"),
                "reading_score": info["reading_score"].get("value"),
                "overall_score": info["overall_score"].get("value"),
                "owner": info.get("owner").get('value'),
                # "mother_tongue": info["mother_tongue"].get("value"),
            }

            out.append(customer_lang_score)
        return out

    @classmethod
    def update(cls, data, user):
        # CustomerLanguageScore.objects.filter(user=user).delete()
        obj_data = cls.extract_lang_data(data)
        serializer = serializers.CustomerLanguageUpdateSerializer(data=obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        enum_validated_data = dict(enumerate(validated_data))
        count = 0
        try:
            for ids in obj_data:
                validated_data_from_dict = enum_validated_data[count]
                CustomerLanguageScore.objects.update_or_create(id=ids.get('id'),
                                                               defaults={
                                                                 "test_type": validated_data_from_dict.get('test_type'),
                                                                 "test_date": validated_data_from_dict.get('test_date'),
                                                                 "result_date": validated_data_from_dict.get('result_date'),
                                                                 "test_version": validated_data_from_dict.get('test_version'),
                                                                 "report_form_number": validated_data_from_dict.get('report_form_number'),
                                                                 "listening_score": validated_data_from_dict.get('listening_score'),
                                                                 "writing_score": validated_data_from_dict.get('writing_score'),
                                                                 "speaking_score": validated_data_from_dict.get('speaking_score'),
                                                                 "reading_score": validated_data_from_dict.get('reading_score'),
                                                                 "overall_score": validated_data_from_dict.get('overall_score'),
                                                                 "user": user,
                                                                 "owner": validated_data_from_dict.get(
                                                                       'owner'),
                                                                 })
                count += 1
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:LanguageScore:update_lang_score ' + str(e))
            return True, str(e)
        return False, ''


class SpouseProfileView(GenericViewSet):

    @classmethod
    def extract_spouse_data(cls, data):

        customer_lang_score = {
            "id": data.get("id"),
            "first_name": data["first_name"].get("value"),
            "last_name": data["last_name"].get("value"),
            "age": data["age"].get("value"),
            "date_of_marriage": data["date_of_marriage"].get("value"),
            "number_of_children": data["number_of_children"].get("value"),
            "mother_fullname": data["mother_fullname"].get("value"),
            "father_fullname": data["father_fullname"].get("value"),
            "passport_number": data["passport_number"].get("value"),
            "passport_country": data["passport_country"].get("value"),
            "passport_issue_date": data["passport_issue_date"].get("value"),
            "passport_expiry_date": data["passport_expiry_date"].get("value"),
            }

        return customer_lang_score

    @classmethod
    def update(cls, data, user):
        # CustomerSpouseProfile.objects.filter(customer__user=user).delete()
        obj_data = cls.extract_spouse_data(data)
        serializer = serializers.CustomerSpouseProfileUpdateSerializer(data=obj_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            CustomerSpouseProfile.objects.update_or_create(id=obj_data.get('id'),
                                                           defaults={
                                                             "date_of_marriage": validated_data.get('date_of_marriage'),
                                                             "number_of_children": validated_data.get('number_of_children'),
                                                             "first_name": validated_data.get('first_name'),
                                                             "last_name": validated_data.get('last_name'),
                                                             "mother_fullname": validated_data.get('mother_fullname'),
                                                             "father_fullname": validated_data.get('father_fullname'),
                                                             "age": validated_data.get('age'),
                                                             "passport_number": validated_data.get('passport_number'),
                                                             "passport_country": validated_data.get('passport_country'),
                                                             "passport_issue_date": validated_data.get('passport_issue_date'),
                                                             "passport_expiry_date": validated_data.get('passport_expiry_date'),
                                                             "customer": user.user_profile
                                                             })
            # count += 1
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:LanguageScore:update_spouse_profile ' + str(e))
            return True, str(e)
        return False, ''


class FamilyInformationView(GenericViewSet):

    @classmethod
    def extract_family_data(cls, data):
        out = []
        for info in data:
            family_data = {
                "id": info.get("id"),
                "relationship": info["relationship"].get("value"),
                "first_name": info["first_name"].get("value"),
                "last_name": info["last_name"].get("value"),
                "date_of_birth": info["date_of_birth"].get("value"),
                "date_of_death": info["date_of_death"].get("value"),
                "city_of_birth": info.get("city_of_birth").get("value"),
                "country_of_birth": info["country_of_birth"].get("value"),
                "street_address": info["street_address"].get("value"),
                "current_country": info["current_country"].get("value"),
                "current_state": info["current_state"].get("value"),
                "current_occupation": info["current_occupation"].get("value"),
            }
            if family_data['date_of_death'] == '':
                del family_data['date_of_death']
            out.append(family_data)
        return out

    @classmethod
    def update(cls, data, user):
        # CustomerFamilyInformation.objects.filter(customer__user=user).delete()
        obj_data = cls.extract_family_data(data)
        serializer = serializers.CustomerFamilyInfoUpdateSerializer(data=obj_data, many=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        enum_validated_data = dict(enumerate(validated_data))
        count = 0
        try:
            for ids in obj_data:
                validated_data_from_dict = enum_validated_data[count]
                CustomerFamilyInformation.objects.update_or_create(id=ids.get('id'),
                                                       defaults={
                                                         "relationship": validated_data_from_dict.get('relationship'),
                                                         "first_name": validated_data_from_dict.get('first_name'),
                                                         "last_name": validated_data_from_dict.get('last_name'),
                                                         "date_of_birth": validated_data_from_dict.get('date_of_birth'),
                                                         "date_of_death": validated_data_from_dict.get('date_of_death'),
                                                         "city_of_birth": validated_data_from_dict.get('city_of_birth'),
                                                         "country_of_birth": validated_data_from_dict.get('country_of_birth'),
                                                         "street_address": validated_data_from_dict.get('street_address'),
                                                         "current_country": validated_data_from_dict.get('current_country'),
                                                         "current_state": validated_data_from_dict.get('current_state'),
                                                         "current_occupation": validated_data_from_dict.get('current_occupation'),
                                                         "customer": user.user_profile
                                                         })
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:FamilyInfo:update_family_information ' + str(e))
            return True, str(e)
        return False, ''


class CustomerInformationView(GenericViewSet):
    @classmethod
    def extract(cls, datas):
        profile = {
            "first_name": datas['first_name'].get("value"),
            "last_name": datas['last_name'].get("value"),
            "mother_fullname": datas['mother_fullname'].get("value"),
            "father_fullname": datas['father_fullname'].get("value"),
            "age": datas['age'].get("value"),
            "address": datas['address'].get("value"),
            "phone_number": datas['phone_number'].get("value"),
            # "date_of_birth": datas['date_of_birth'].get("value"),
            "current_country": datas['current_country'].get("value"),
            "desired_country": datas['desired_country'].get("value"),

            "height": datas['height'].get("value"),
            "previous_marriage": datas['any_previous_marriage'].get("value"),
            "eye_color": datas['eye_color'].get("value"),
            "first_language": datas['first_language'].get("value"),
            "city_of_birth": datas['city_of_birth'].get("value"),
            "email": datas['email'].get("value"),
            "funds_available": datas['funds_available'].get("value"),
            "marital_status": datas['marital_status'].get("value"),

            "type_of_visa": datas['type_of_visa'].get("value"),
            "passport_number": datas['passport_number'].get("value"),
            "passport_country": datas['passport_country'].get("value"),
            "passport_issue_date": datas['passport_issue_date'].get("value"),
            "passport_expiry_date": datas['passport_expiry_date'].get("value"),
        }
        return profile

    @classmethod
    def update(cls, data, user):
        obj_data = cls.extract(data)
        serializer = serializers.CustomerUpdateProfileSerializer(data=obj_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['user'] = user
        try:
            serializer.save()
            user.phone_number = obj_data.get('phone_number')
            user.save()
        except Exception as e:
            logger.error('ERROR: AUTHENTICATION:ProfileView ' + str(e))
            return True, str(e)
        return False, ''
