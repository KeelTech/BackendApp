import base64
import json
import random
import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from keel.account import models as account_models
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from dal import autocomplete
from rest_framework import mixins, viewsets, status
from keel.api.v1.auth import serializers
from rest_framework.response import Response
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.db.models import F, Sum, Max, Q, Prefetch, Case, When, Count, Value
from django.db.models.functions import Concat, Substr
from django.forms.models import model_to_dict

from keel.common.middleware import use_slave
from keel.common.models import UserConfig, PaymentOptions, AppointmentHistory, BlacklistUser, BlockedStates
from keel.common.utils import get_all_upcoming_appointments
from keel.coupon.models import UserSpecificCoupon, Coupon
from keel.lead.models import UserLead
from keel.plus.models import PlusAppointmentMapping, PlusUser, PlusPlans, PlusDummyData, PlusMembers
from keel.plus.usage_criteria import get_price_reference, get_class_reference
from keel.sms.api import send_otp
from keel.doctor.models import DoctorMobile, Doctor, HospitalNetwork, Hospital, DoctorHospital, DoctorClinic, \
                                DoctorClinicTiming, ProviderSignupLead
from keel.authentication.models import (OtpVerifications, NotificationEndpoint, Notification, UserProfile,
                                         Address, AppointmentTransaction, GenericAdmin, UserSecretKey, GenericLabAdmin,
                                         AgentToken, DoctorNumber, LastLoginTimestamp, UserProfileEmailUpdate,
                                         WhiteListedLoginTokens)
from keel.notification.models import SmsNotification, EmailNotification, WhtsappNotification
from keel.account.models import PgTransaction, ConsumerAccount, ConsumerTransaction, Order, ConsumerRefund, OrderLog, \
    UserReferrals, UserReferred, PgLogs, PaymentProcessStatus
from keel.account.mongo_models import PgLogs as mongo_pglogs
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from keel.api.pagination import paginate_queryset
from keel.api.v1 import utils
from keel.doctor.models import OpdAppointment
from keel.api.v1.doctor.serializers import (OpdAppointmentSerializer, AppointmentFilterUserSerializer,
                                             UpdateStatusSerializer, CreateAppointmentSerializer,
                                             AppointmentRetrieveSerializer, OpdAppTransactionModelSerializer,
                                             OpdAppModelSerializer, OpdAppointmentUpcoming,
                                             NewAppointmentRetrieveSerializer)
from keel.api.v1.diagnostic.serializers import (LabAppointmentModelSerializer,
                                                 LabAppointmentRetrieveSerializer, LabAppointmentCreateSerializer,
                                                 LabAppTransactionModelSerializer, LabAppRescheduleModelSerializer,
                                                 LabAppointmentUpcoming)
from keel.api.v1.insurance.serializers import (InsuranceTransactionSerializer)
from keel.api.v1.diagnostic.views import LabAppointmentView
from keel.diagnostic.models import (Lab, LabAppointment, AvailableLabTest, LabNetwork)
from keel.payout.models import Outstanding
from keel.authentication.backends import JWTAuthentication, BajajAllianzAuthentication, MatrixUserAuthentication, SbiGAuthentication, RefreshAuthentication
from keel.api.v1.utils import (IsConsumer, IsDoctor, opdappointment_transform, labappointment_transform,
                                ErrorCodeMapping, IsNotAgent, GenericAdminEntity, generate_short_url, form_time_slot)
from django.conf import settings
from collections import defaultdict
import copy
import logging
import jwt
from keel.insurance.models import InsuranceTransaction, UserInsurance, InsuredMembers
from decimal import Decimal
from keel.web.models import ContactUs
from keel.notification.tasks import send_pg_acknowledge, save_pg_response, save_payment_status

from keel.ratings_review import models as rate_models
from django.contrib.contenttypes.models import ContentType

import re
from keel.matrix.tasks import push_order_to_matrix



logger = logging.getLogger(__name__)
User = get_user_model()


def expire_otp(phone_number):
    OtpVerifications.objects.filter(phone_number=phone_number).update(is_expired=True)


class LoginOTP(GenericViewSet):

    authentication_classes = []
    serializer_class = serializers.OTPSerializer

    @transaction.atomic
    def generate(self, request, format=None):
        response = {'exists': 0}
        # if request.data.get("phone_number"):
        #     expire_otp(phone_number=request.data.get("phone_number"))
        serializer = serializers.OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone_number = data['phone_number']

        otp_obj = data.get('otp_obj')
        # otp_obj = OtpVerifications.objects.filter(phone_number=phone_number).order_by('-id').first()
        if data.get('via_whatsapp', False) and otp_obj and not otp_obj.can_send():
            return Response({'success': False})

        blocked_state = BlacklistUser.get_state_by_number(phone_number, BlockedStates.States.LOGIN)
        if blocked_state:
            return Response({'error': blocked_state.message}, status=status.HTTP_400_BAD_REQUEST)
        req_type = request.query_params.get('type')
        via_sms = data.get('via_sms', True)
        via_whatsapp = data.get('via_whatsapp', False)
        call_source = data.get('request_source')
        retry_send = request.query_params.get('retry', False)
        otp_message = OtpVerifications.get_otp_message(request.META.get('HTTP_PLATFORM'), req_type, version=request.META.get('HTTP_APP_VERSION'))
        if req_type == 'doctor':
            doctor_queryset = GenericAdmin.objects.select_related('doctor', 'hospital').filter(phone_number=phone_number, is_disabled=False)
            lab_queryset = GenericLabAdmin.objects.select_related('lab', 'lab_network').filter(
                Q(phone_number=phone_number, is_disabled=False),
                (Q(lab__isnull=True, lab_network__data_status=LabNetwork.QC_APPROVED) |
                 Q(lab__isnull=False,
                   lab__data_status=Lab.QC_APPROVED, lab__onboarding_status=Lab.ONBOARDED
                   )
                 )
                )
            provider_signup_queryset = ProviderSignupLead.objects.filter(phone_number=phone_number, user__isnull=False)

            if lab_queryset.exists() or doctor_queryset.exists() or provider_signup_queryset.exists():
                response['exists'] = 1
                send_otp(otp_message, phone_number, retry_send, via_sms=via_sms, via_whatsapp=via_whatsapp, call_source=call_source)

            # if queryset.exists():
            #     response['exists'] = 1
            #     send_otp("OTP for DocPrime login is {}", phone_number)

        else:
            send_otp(otp_message, phone_number, retry_send, via_sms=via_sms, via_whatsapp=via_whatsapp, call_source=call_source)
            if User.objects.filter(phone_number=phone_number, user_type=User.CONSUMER).exists():
                response['exists'] = 1

        return Response(response)

    def verify(self, request, format=None):

        serializer = serializers.OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": "OTP Generated Sucessfuly."})


class UserViewset(GenericViewSet):
    serializer_class = serializers.UserSerializer
    @transaction.atomic
    def login(self, request, format=None):
        from keel.authentication.backends import JWTAuthentication
        serializer = serializers.OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_exists = 1
        user = User.objects.filter(phone_number=data['phone_number'], user_type=User.CONSUMER).first()
        if not user:
            user_exists = 0
            user = User.objects.create(phone_number=data['phone_number'],
                                       is_phone_number_verified=True,
                                       user_type=User.CONSUMER)

            # for new user, create a referral coupon entry
            self.set_referral(user)

        self.set_coupons(user)

        token_object = JWTAuthentication.generate_token(user, request)

        expire_otp(data['phone_number'])

        response = {
            "login": 1,
            "user_exists": user_exists,
            "user_id": user.id,
            "token": token_object['token'],
            "exp": token_object['payload']['exp']
        }
        return Response(response)

    def set_coupons(self, user):
        UserSpecificCoupon.objects.filter(phone_number=user.phone_number, user__isnull=True).update(user=user)

    def set_referral(self, user):
        try:
            UserReferrals.objects.create(user=user)
        except Exception as e:
            logger.error(str(e))

    @transaction.atomic
    def register(self, request, format=None):

        data = {'phone_number':request.data.get('phone_number'),'otp':request.data.get('otp')}
        # data['profile'] = {
        #     'name': request.data.get('name'),
        #     'age': request.data.get('age'),
        #     'gender': request.data.get('gender'),
        #     'email': request.data.get('email'),
        # }

        serializer = serializers.UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = Token.objects.get_or_create(user=user)

        expire_otp(data['phone_number'])

        response = {
            "login":1,
            "token" : str(token[0])
        }
        return Response(response)

    @transaction.atomic
    def logout(self, request):
        required_token = request.data.get("token", None)
        if required_token and request.user.is_authenticated:
            NotificationEndpoint.objects.filter(user=request.user, token=request.data.get("token")).delete()
        # WhiteListedLoginTokens.objects.filter(token=required_token).delete()
        return Response({"message": "success"})

    @transaction.atomic
    def doctor_login(self, request, format=None):
        serializer = serializers.DoctorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone_number = data['phone_number']
        user = User.objects.filter(phone_number=phone_number, user_type=User.DOCTOR).first()

        if not user:
            user = User.objects.create(phone_number=data['phone_number'], is_phone_number_verified=True,
                                       user_type=User.DOCTOR)
            # doctor_mobile = DoctorMobile.objects.filter(number=phone_number, is_primary=True)
        if not hasattr(user, 'doctor'):
            doctor_mobile = DoctorNumber.objects.filter(phone_number=phone_number)
            if doctor_mobile.exists():
                doctor = doctor_mobile.first().doctor
                doctor.user = user
                doctor.save()

        GenericAdmin.update_user_admin(phone_number)
        GenericLabAdmin.update_user_lab_admin(phone_number)
        self.update_live_status(phone_number)

        token_object = JWTAuthentication.generate_token(user, request)
        expire_otp(data['phone_number'])

        if data.get("source"):
            LastLoginTimestamp.objects.create(user=user, source=data.get("source"))

        response = {
            "login": 1,
            "user_id": user.id,
            "token": token_object['token'],
            "expiration_time": token_object['payload']['exp']
        }
        return Response(response)

    def update_live_status(self, phone):
        queryset = GenericAdmin.objects.select_related('doctor').filter(phone_number=phone)
        if queryset.first():
            for admin in queryset.distinct('doctor').all():
                if admin.doctor is not None:
                    if not admin.doctor.is_live:
                        if admin.doctor.data_status == Doctor.QC_APPROVED and admin.doctor.onboarding_status == Doctor.ONBOARDED:
                            admin.doctor.is_live = True
                            admin.doctor.live_at = datetime.datetime.now()
                            admin.doctor.save()
                elif admin.hospital:
                    for hosp_doc in admin.hospital.assoc_doctors.all():
                        if hosp_doc.data_status == Doctor.QC_APPROVED and hosp_doc.onboarding_status == Doctor.ONBOARDED:
                            hosp_doc.is_live = True
                            hosp_doc.live_at= datetime.datetime.now()
                            hosp_doc.save()


class NotificationEndpointViewSet(GenericViewSet):
    serializer_class = serializers.NotificationEndpointSerializer
    permission_classes = (IsNotAgent, )

    @transaction.atomic
    def save(self, request):
        serializer = serializers.NotificationEndpointSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        NotificationEndpoint.objects.filter(token=validated_data.get('token')).delete()
        notification_endpoint_data = {
            "user": request.user.id,
            "device_id": validated_data.get("device_id"),
            "platform": validated_data.get("platform"),
            "app_name": validated_data.get("app_name"),
            "app_version": validated_data.get("app_version"),
            "token": validated_data.get("token")
        }
        notification_endpoint_serializer = serializers.NotificationEndpointSerializer(data=notification_endpoint_data)
        notification_endpoint_serializer.is_valid(raise_exception=True)
        try:
            notification_endpoint_serializer.save()
        except IntegrityError:
            return Response(notification_endpoint_serializer.data)
        return Response(notification_endpoint_serializer.data)

    def delete(self, request):
        serializer = serializers.NotificationEndpointDeleteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        notification_endpoint = NotificationEndpoint.objects.filter(token=validated_data.get('token')).first()
        notification_endpoint.delete()
        return Response(data={"status": 1, "message": "deleted"})


class NotificationViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsNotAgent)

    def list(self, request):
        queryset = paginate_queryset(queryset=Notification.objects.filter(user=request.user),
                                     request=request)
        serializer = serializers.NotificationSerializer(queryset, many=True)
        return Response(serializer.data)


class WhatsappOptinViewSet(GenericViewSet):

    def update(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        optin = request.data.get('optin')
        source = request.data.get('source')

        if optin not in [True, False]:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'optin must be boolean field.'})

        if not phone_number:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'phone_number is required.'})

        user_profile_obj = UserProfile.objects.filter(phone_number=phone_number)
        if not user_profile_obj:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'could not find the userprofile with number %s' % str(phone_number)})

        if source == 'WHATSAPP_SERVICE' and optin is False:
            user_profile_obj.update(whatsapp_optin=optin, whatsapp_is_declined=True)

        return Response()


class UserProfileViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                         GenericViewSet):

    serializer_class = serializers.UserProfileSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsConsumer)
    pagination_class = None

    def get_queryset(self):
        request = self.request
        queryset = UserProfile.objects.filter(user=request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        serializer = [serializers.UserProfileSerializer(q, context= {'request':request}).data for q in qs]
        result = list()
        result.extend(list(filter(lambda x: (x['is_default_user'] and x['is_vip_gold_member']) or x['is_default_user'], serializer)))
        result.extend(list(filter(lambda x: x['is_vip_gold_member'] and not x['is_default_user'], serializer)))
        result.extend(list(filter(lambda x: not x['is_default_user'] and not x['is_vip_gold_member'], serializer)))

        return Response(data=result)

    def create(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = {}
        data['name'] = request.data.get('name')
        data['gender'] = request.data.get('gender')
        # data['age'] = request.data.get('age')
        data['email'] = request.data.get('email')
        data['phone_number'] = request.data.get('phone_number')
        data['whatsapp_optin'] = request.data.get('whatsapp_optin')
        data['user'] = request.user.id
        first_profile = False
        add_to_gold_members = request.data.get('add_to_gold')

        if not queryset.exists():
            data.update({
                "is_default_user": True
            })
            first_profile = True

        if not bool(re.match(r"^[a-zA-Z ]+$", request.data.get('name'))):
            return Response({"error": "Invalid Name"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('age'):
            try:
                age = int(request.data.get("age"))
                data['dob'] = datetime.datetime.now() - relativedelta(years=age)
                data['dob'] = data['dob'].date()
            except:
                return Response({"error": "Invalid Age"}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data.get('dob'):
            dob = request.data.get('dob')
            data['dob'] = dob
        else:
            # return Response({'age': {'code': 'required', 'message': 'This field is required.'}},
            #                 status=status.HTTP_400_BAD_REQUEST)
            data['dob'] = None


        if not data.get('phone_number'):
            data['phone_number'] = request.user.phone_number

        if add_to_gold_members:
            default_profile = request.user.get_default_profile()
            if default_profile.email and not data.get('email'):
                data['email'] = default_profile.email

        serializer = serializers.UserProfileSerializer(data=data, context= {'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.validated_data
        if UserProfile.objects.filter(name__iexact=data['name'], user=request.user).exists():
            # return Response({
            #     "request_errors": {"code": "invalid",
            #                        "message": "Profile with the given name already exists."
            #                        }
            # }, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)


        serializer.save()

        if add_to_gold_members:
            saved_profile = request.user.profiles.filter().order_by('-created_at').first()
            request.user.active_plus_user.add_user_profile_to_members(saved_profile)

        # for new profile credit referral amount if any refrral code is used
        if first_profile and request.data.get('referral_code'):
            try:
                self.credit_referral(request.data.get('referral_code'), request.user)
            except Exception as e:
                logger.error(str(e))
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = {key: value for key, value in request.data.items()}
        # if data.get('age'):
        #     try:
        #         age = int(request.data.get("age"))
        #         data['dob'] = datetime.datetime.now() - relativedelta(years=age)
        #         data['dob'] = data['dob'].date()
        #     except:
        #         return Response({"error": "Invalid Age"}, status=status.HTTP_400_BAD_REQUEST)

        obj = self.get_object()

        add_to_gold_members = data.get('add_to_gold')
        if add_to_gold_members:
            default_profile = request.user.get_default_profile()
            if default_profile.email and not data.get('email'):
                data['email'] = default_profile.email

        plus_user_obj = request.user.active_plus_user
        associated_plus_member = None
        if plus_user_obj:
            associated_plus_member = PlusMembers.objects.filter(plus_user=plus_user_obj, profile=obj).first()

        if associated_plus_member and data.get('name') and data.get('name') != obj.name:
            return Response({
                "request_errors": {"code": "invalid",
                                   "message": "Profile covered in the gold cannot edit their name."
                                   }
            }, status=status.HTTP_400_BAD_REQUEST)

        if not bool(re.match(r"^[a-zA-Z ]+$", data.get('name'))):
            return Response({"error": "Invalid Name"}, status=status.HTTP_400_BAD_REQUEST)
        
        if data.get("name") and UserProfile.objects.exclude(id=obj.id).filter(name=data['name'],
                                                                              user=request.user).exists():
            return Response({
                "request_errors": {"code": "invalid",
                                   "message": "Profile with the given name already exists."
                                   }
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.UserProfileSerializer(obj, data=data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # Insurance work. User is made to update only whatsapp_optin and whatsapp_is_declined in case if userprofile
        # is covered under insuranc. Else profile under insurance  cannot be updated in any case.

        insured_member_obj = InsuredMembers.objects.filter(profile__id=obj.id).last()
        insured_member_profile = None
        insured_member_status = None
        if insured_member_obj:
            insured_member_profile = insured_member_obj.profile
            insured_member_status = insured_member_obj.user_insurance.status
        # if obj and hasattr(obj, 'id') and obj.id and insured_member_profile:

        if request.user and request.user.active_insurance and data.get('is_default_user') and data.get('is_default_user') != obj.is_default_user:
            return Response({
                "request_errors": {"code": "invalid",
                                   "message": "Any Profile or user associated with the insurance cannot change default user."
                                   }})

        if obj and hasattr(obj, 'id') and obj.id and insured_member_profile and not (insured_member_status == UserInsurance.CANCELLED or
                                                              insured_member_status == UserInsurance.EXPIRED):

            whatsapp_optin = data.get('whatsapp_optin')
            whatsapp_is_declined = data.get('whatsapp_is_declined')

            if (whatsapp_optin and whatsapp_optin in [True, False] and whatsapp_optin != insured_member_profile.whatsapp_optin) or \
                    (whatsapp_is_declined and whatsapp_is_declined in [True, False] and whatsapp_is_declined != insured_member_profile.whatsapp_is_declined):
                if whatsapp_optin:
                    insured_member_profile.whatsapp_optin = whatsapp_optin
                if whatsapp_is_declined:
                    insured_member_profile.whatsapp_is_declined = whatsapp_is_declined

                insured_member_profile.save()
                return Response(serializer.data)
            else:
                return Response({
                    "request_errors": {"code": "invalid",
                                       "message": "Profile cannot be changed which are covered under insurance."
                                       }
                }, status=status.HTTP_400_BAD_REQUEST)
        if data.get('is_default_user', None):
            UserProfile.objects.filter(user=obj.user).update(is_default_user=False)
        else:
            primary_profile = UserProfile.objects.filter(user=obj.user, is_default_user=True).first()
            if not primary_profile or obj.id == primary_profile.id:
                return Response({
                    "request_errors": {"code": "invalid",
                                       "message": "Atleast one profile should be selected as primary."
                                       }
                }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        if add_to_gold_members:
            saved_profile = request.user.profiles.filter().order_by('-updated_at').first()
            request.user.active_plus_user.add_user_profile_to_members(saved_profile)

        return Response(serializer.data)

    def upload(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.UploadProfilePictureSerializer(instance, data=request.data, context= {'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @transaction.atomic()
    def credit_referral(self, referral_code, user):
        referral = UserReferrals.objects.filter(Q(code__iexact=referral_code), ~Q(user=user)).first()
        if referral and not UserReferred.objects.filter(user=user).exists():
            UserReferred.objects.create(user=user, referral_code=referral, used=False)
            ConsumerAccount.credit_referral(user, UserReferrals.SIGNUP_CASHBACK)

class keelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    pass


class ReferralViewSet(GenericViewSet):
    # authentication_classes = (JWTAuthentication, )
    # permission_classes = (IsAuthenticated, IsNotAgent)

    @use_slave
    def retrieve(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"status": 0}, status=status.HTTP_401_UNAUTHORIZED)
        referral = UserReferrals.objects.filter(user=user).first()
        if not referral:
            referral = UserReferrals()
            referral.user = user
            referral.save()

        user_config = UserConfig.objects.filter(key="referral").first()
        help_flow = []
        share_text = ''
        share_url = ''
        whatsapp_text = ''
        referral_amt = ''
        if user_config:
            all_data = user_config.data
            help_flow = all_data.get('help_flow', [])
            share_text = all_data.get('share_text', '').replace('$referral_code', referral.code)
            share_url = all_data.get('share_url', '').replace('$referral_code', referral.code)
            whatsapp_text = all_data.get('whatsapp_text', '').replace('$referral_code', referral.code)
            referral_amt = all_data.get('referral_amt', '')

        return Response({"code": referral.code, "status": 1, 'help_flow': help_flow,
                         "share_text": share_text, "share_url": share_url, 'whatsapp_text': whatsapp_text,
                         "referral_amt": referral_amt})

    def retrieve_by_code(self, request, code):
        referral = UserReferrals.objects.filter(code__iexact=code).first()
        if referral:
            default_user_profile = UserProfile.objects.filter(user=referral.user, is_default_user=True).first()
            if default_user_profile:
                return Response({"name": default_user_profile.name, "status": 1})

        return Response({"status": 0}, status=status.HTTP_404_NOT_FOUND)

    def get_referral_amt(self, request):
        user_config = UserConfig.objects.filter(key="referral").first()
        resp = {"referral_amt": ''}
        if user_config:
            all_data = user_config.data
            resp['referral_amt'] = all_data.get('referral_amt', '')
            return Response(resp)
        return Response(resp)


class UserAppointmentsViewSet(keelViewSet):

    serializer_class = OpdAppointmentSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsConsumer, )

    def get_queryset(self):
        user = self.request.user
        return OpdAppointment.objects.filter(user=user)

    @transaction.non_atomic_requests
    @use_slave
    def list(self, request):
        params = request.query_params
        doctor_serializer = self.doctor_appointment_list(request, params)
        lab_serializer = self.lab_appointment_list(request, params)
        combined_data = list()
        if doctor_serializer.data:
            combined_data.extend(doctor_serializer.data)
        if lab_serializer.data:
            combined_data.extend(lab_serializer.data)
        combined_data = sorted(combined_data, key=lambda x: x['time_slot_start'], reverse=True)
        # temp_dict = dict()
        # for data in combined_data:
        #     if not temp_dict.get(data["status"]):
        #         temp_dict[data["status"]] = [data]
        #     else:
        #         temp_dict[data["status"]].append(data)
        # combined_data = list()
        # status_six_data = list()
        # for k, v in sorted(temp_dict.items(), key=lambda x: x[0]):
        #     if k==6:
        #         status_six_data.extend(v)
        #     else:
        #         combined_data.extend(v)
        # combined_data.extend(status_six_data)
        combined_data = combined_data[:200]
        return Response(combined_data)

    @transaction.non_atomic_requests
    def retrieve(self, request, pk=None):
        user = request.user
        input_serializer = serializers.AppointmentqueryRetrieveSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        appointment_type = input_serializer.validated_data.get('type')
        if appointment_type == 'lab':
            queryset = LabAppointment.objects.filter(pk=pk, user=user)
            serializer = LabAppointmentRetrieveSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        elif appointment_type == 'doctor':
            queryset = OpdAppointment.objects.filter(pk=pk, user=user)
            # serializer = AppointmentRetrieveSerializer(queryset, many=True, context={"request": request})
            serializer = NewAppointmentRetrieveSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            return Response({'Error': 'Invalid Request Type'})

    @transaction.atomic
    def update(self, request, pk=None):
        serializer = UpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        query_input_serializer = serializers.AppointmentqueryRetrieveSerializer(data=request.query_params)
        query_input_serializer.is_valid(raise_exception=True)
        source = ''
        responsible_user = None
        if validated_data.get('source', None):
            source = validated_data.get('source')
        if query_input_serializer.validated_data.get('source', None):
            source = query_input_serializer.validated_data.get('source')
        if request.user and hasattr(request.user, 'user_type'):
            responsible_user = request.user
            if not source:
                if request.user.user_type == User.DOCTOR:
                    source = AppointmentHistory.DOC_APP
                elif request.user.user_type == User.CONSUMER:
                    source = AppointmentHistory.CONSUMER_APP
        appointment_type = query_input_serializer.validated_data.get('type')
        if appointment_type == 'lab':
            # lab_appointment = get_object_or_404(LabAppointment, pk=pk)
            lab_appointment = LabAppointment.objects.select_for_update().filter(pk=pk).first()
            lab_appointment._source = source
            lab_appointment._responsible_user = responsible_user
            resp = dict()
            if not lab_appointment:
                resp["status"] = 0
                resp["message"] = "Invalid appointment Id"
                return Response(resp, status.HTTP_404_NOT_FOUND)
            allowed = lab_appointment.allowed_action(request.user.user_type, request)
            appt_status = validated_data.get('status')
            if appt_status not in allowed:
                resp = dict()
                resp['allowed'] = allowed
                resp['Error'] = 'Action Not Allowed'
                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            updated_lab_appointment = self.lab_appointment_update(request, lab_appointment, validated_data)
            if updated_lab_appointment.get("status") is not None and updated_lab_appointment["status"] == 0:
                return Response(updated_lab_appointment, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(updated_lab_appointment)
        elif appointment_type == 'doctor':
            # opd_appointment = get_object_or_404(OpdAppointment, pk=pk)
            opd_appointment = OpdAppointment.objects.select_for_update().filter(pk=pk).first()
            opd_appointment._source = source
            opd_appointment._responsible_user = responsible_user
            resp = dict()
            if not opd_appointment:
                resp["status"] = 0
                resp["message"] = "Invalid appointment Id"
                return Response(resp, status.HTTP_404_NOT_FOUND)
            allowed = opd_appointment.allowed_action(request.user.user_type, request)
            appt_status = validated_data.get('status')
            if appt_status not in allowed:
                resp['allowed'] = allowed
                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            updated_opd_appointment = self.doctor_appointment_update(request, opd_appointment, validated_data)
            if updated_opd_appointment.get("status") is not None and updated_opd_appointment["status"] == 0:
                return Response(updated_opd_appointment, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(updated_opd_appointment)

    @transaction.atomic
    def lab_appointment_update(self, request, lab_appointment, validated_data):
        resp = dict()
        resp["status"] = 1
        selected_timings_type = ""
        if validated_data.get('status'):
            if validated_data['status'] == LabAppointment.CANCELLED:
                lab_appointment.cancellation_type = LabAppointment.PATIENT_CANCELLED
                lab_appointment.cancellation_reason = validated_data.get('cancellation_reason', None)
                lab_appointment.cancellation_comments = validated_data.get('cancellation_comment', '')
                lab_appointment.action_cancelled(request.data.get('refund', 1))
                resp = LabAppointmentRetrieveSerializer(lab_appointment, context={"request": request}).data
            elif validated_data.get('status') == LabAppointment.RESCHEDULED_PATIENT:
                test_time_slots = []
                if validated_data.get('multi_timings_enabled'):
                    same_time_slot_err = True
                    selected_timings_type = validated_data.get('selected_timings_type', 'separate')
                    lab_appointment_tests = lab_appointment.test_mappings.all()
                    for test_timing in validated_data.get('test_timings'):
                        appointment_tests = list(filter(lambda x: x.test_id == test_timing.get('test').id, lab_appointment_tests))
                        if not appointment_tests:
                            resp = {
                                "status": 0,
                                "message": "Requested test for appointment is not found."
                            }
                            return resp
                        appointment_test = appointment_tests[0]
                        if test_timing.get("start_date") and test_timing.get('start_time'):
                            time_slot_start = utils.form_time_slot(
                                test_timing.get("start_date"),
                                test_timing.get("start_time"))
                            if not appointment_test.time_slot_start == time_slot_start:
                                same_time_slot_err = False
                            if lab_appointment.payment_type == OpdAppointment.INSURANCE and lab_appointment.insurance_id is not None:
                                user_insurance = UserInsurance.objects.get(id=lab_appointment.insurance_id)
                                if user_insurance:
                                    # insurance_threshold = user_insurance.insurance_plan.threshold.filter().first()
                                    if time_slot_start > user_insurance.expiry_date or not user_insurance.is_valid():
                                        resp = {
                                            "status": 0,
                                            "message": "Appointment time is not covered under insurance"
                                        }
                                        return resp
                            if lab_appointment.payment_type in [OpdAppointment.VIP, OpdAppointment.GOLD] and lab_appointment.plus_plan_id is not None:
                                plus_user = PlusUser.objects.filter(id=lab_appointment.plus_plan_id).first()
                                if plus_user:
                                    if time_slot_start > plus_user.expire_date:
                                        resp = {
                                            "status": 0,
                                            "message": "Appointment time is not covered under VIP/GOLD"
                                        }
                                        return resp

                            test_level_timing = dict()
                            test_level_timing['test_id'] = test_timing.get('test').id
                            test_level_timing['time_slot_start'] = time_slot_start
                            test_time_slots.append(test_level_timing)

                    if same_time_slot_err:
                        resp = {
                            "status": 0,
                            "message": "Cannot Reschedule for same timeslot"
                        }
                        return resp

                    time_slot_start = None
                else:
                    if validated_data.get("start_date") and validated_data.get('start_time'):
                        time_slot_start = utils.form_time_slot(
                            validated_data.get("start_date"),
                            validated_data.get("start_time"))
                        if lab_appointment.time_slot_start == time_slot_start:
                            resp = {
                                "status": 0,
                                "message": "Cannot Reschedule for same timeslot"
                            }
                            return resp
                        if lab_appointment.payment_type == OpdAppointment.INSURANCE and lab_appointment.insurance_id is not None:
                            user_insurance = UserInsurance.objects.get(id=lab_appointment.insurance_id)
                            if user_insurance :
                                # insurance_threshold = user_insurance.insurance_plan.threshold.filter().first()
                                if time_slot_start > user_insurance.expiry_date or not user_insurance.is_valid():
                                    resp = {
                                        "status": 0,
                                        "message": "Appointment time is not covered under insurance"
                                    }
                                    return resp
                        if lab_appointment.payment_type in [OpdAppointment.VIP, OpdAppointment.GOLD] and lab_appointment.plus_plan_id is not None:
                            plus_user = PlusUser.objects.filter(id=lab_appointment.plus_plan_id).first()
                            if plus_user:
                                if time_slot_start > plus_user.expire_date:
                                    resp = {
                                        "status": 0,
                                        "message": "Appointment time is not covered under VIP/GOLD"
                                    }
                                    return resp

                test_ids = lab_appointment.lab_test.values_list('test__id', flat=True)
                lab_test_queryset = AvailableLabTest.objects.select_related('lab_pricing_group__labs').filter(
                    lab_pricing_group__labs=lab_appointment.lab,
                    test__in=test_ids)
                deal_price_calculation = Case(When(custom_deal_price__isnull=True, then=F('computed_deal_price')),
                                              When(custom_deal_price__isnull=False, then=F('custom_deal_price')))
                agreed_price_calculation = Case(When(custom_agreed_price__isnull=True, then=F('computed_agreed_price')),
                                                When(custom_agreed_price__isnull=False, then=F('custom_agreed_price')))
                temp_lab_test = lab_test_queryset.values('lab_pricing_group__labs').annotate(total_mrp=Sum("mrp"),
                                                                                             total_deal_price=Sum(
                                                                                                 deal_price_calculation),
                                                                                             total_agreed_price=Sum(
                                                                                                 agreed_price_calculation))
                # old_deal_price = lab_appointment.deal_price
                # old_effective_price = lab_appointment.effective_price
                coupon_discount = lab_appointment.discount
                # coupon_price = self.get_appointment_coupon_price(old_deal_price, old_effective_price)
                new_deal_price = temp_lab_test[0].get("total_deal_price")

                if lab_appointment.home_pickup_charges:
                    new_deal_price += lab_appointment.home_pickup_charges

                if new_deal_price <= coupon_discount:
                    new_effective_price = 0
                else:
                    convenience_charge = None
                    if lab_appointment.insurance_id is None and lab_appointment.plus_plan_id is None:
                        new_effective_price = new_deal_price - coupon_discount
                    elif lab_appointment.plus_plan_id is not None:
                        plus_user = lab_appointment.user.active_plus_user
                        price_data = {"mrp": temp_lab_test[0].get("total_mrp"),
                                      "deal_price": temp_lab_test[0].get("total_deal_price"),
                                      "cod_deal_price": temp_lab_test[0].get("total_deal_price"),
                                      "fees": temp_lab_test[0].get("total_agreed_price", 0),
                                      "home_pickup_charges": lab_appointment.home_pickup_charges}
                        if plus_user:
                            new_effective_price, convenience_charge = self.get_plus_user_effective_price(plus_user, price_data, "LABTEST")
                        if lab_appointment.plus_plan.plan.is_gold:
                            order_obj = Order.objects.filter(reference_id=lab_appointment.id).first()
                            action_data = order_obj.action_data
                            if action_data:
                                discount = int(action_data.get('discount', 0))
                                if discount and discount > 0:
                                    new_effective_price = (new_effective_price + convenience_charge) - discount
                                else:
                                    new_effective_price = new_effective_price + convenience_charge
                            else:
                                new_effective_price = new_effective_price + convenience_charge
                        else:
                            new_effective_price = lab_appointment.effective_price
                    else:
                        new_effective_price = 0.0
                # new_appointment = dict()

                new_appointment = {
                    "id": lab_appointment.id,
                    "lab": lab_appointment.lab,
                    "user": lab_appointment.user,
                    "profile": lab_appointment.profile,
                    "price": temp_lab_test[0].get("total_mrp"),
                    "agreed_price": temp_lab_test[0].get("total_agreed_price", 0),
                    "deal_price": new_deal_price,
                    "effective_price": new_effective_price,
                    "time_slot_start": time_slot_start,
                    "test_time_slots": test_time_slots,
                    "selected_timings_type": selected_timings_type,
                    "profile_detail": lab_appointment.profile_detail,
                    "status": lab_appointment.status,
                    "payment_type": lab_appointment.payment_type,
                    "lab_test": lab_appointment.lab_test,
                    "discount": coupon_discount
                }

                resp = self.extract_payment_details(request, lab_appointment, new_appointment,
                                                    account_models.Order.LAB_PRODUCT_ID)
        return resp

    def get_plus_user_effective_price(self, plus_user, price_data, entity):
        from keel.plus.models import PlusPlans
        if entity == "LABTEST":
            price_engine = get_price_reference(plus_user, "LABTEST")
            if not price_engine:
                price = int(price_data.get('mrp', None))
            else:
                price = price_engine.get_price(price_data)
            # convenience_charge = plus_user.plan.get_convenience_charge(price, "LABTEST")
            plan = plus_user.plan if plus_user else None
            convenience_charge = PlusPlans.get_default_convenience_amount(price_data, "LABTEST", default_plan_query=plan)
            engine = get_class_reference(plus_user, "LABTEST")
            final_price = price + price_data.get('home_pickup_charges', 0)
            mrp_with_home_pickup = price_data.get('mrp') + price_data.get('home_pickup_charges', 0)
            plus_data = engine.validate_booking_entity(cost=final_price, mrp=mrp_with_home_pickup,
                                                       deal_price=price_data.get('deal_price'), price_engine_price=price)
            effective_price = plus_data.get('amount_to_be_paid', None)
            return effective_price, convenience_charge
        else:
            price_engine = get_price_reference(plus_user, "DOCTOR")
            if not price_engine:
                price = int(price_data.get('mrp', None))
            else:
                price = price_engine.get_price(price_data)
            # convenience_charge = plus_user.plan.get_convenience_charge(price, "DOCTOR")
            plan = plus_user.plan if plus_user else None
            convenience_charge = PlusPlans.get_default_convenience_amount(price_data, "DOCTOR",
                                                                          default_plan_query=plan)

            engine = get_class_reference(plus_user, "DOCTOR")
            plus_data = engine.validate_booking_entity(cost=price, mrp=price_data.get('mrp', None),
                                                       deal_price=price_data.get('deal_price'))
            effective_price = plus_data.get('amount_to_be_paid', None)
            return effective_price, convenience_charge

    @transaction.atomic
    def doctor_appointment_update(self, request, opd_appointment, validated_data):
        if validated_data.get('status'):
            resp = dict()
            resp["status"] = 1
            if validated_data['status'] == OpdAppointment.CANCELLED:
                logger.warning("Starting to cancel for id - " + str(opd_appointment.id) + " timezone - " + str(timezone.now()))
                opd_appointment.cancellation_type = OpdAppointment.PATIENT_CANCELLED
                opd_appointment.cancellation_reason = validated_data.get('cancellation_reason', None)
                opd_appointment.cancellation_comments = validated_data.get('cancellation_comment', '')
                opd_appointment.action_cancelled(request.data.get("refund", 1))
                logger.warning(
                    "Ending for id - " + str(opd_appointment.id) + " timezone - " + str(timezone.now()))
                resp = AppointmentRetrieveSerializer(opd_appointment, context={"request": request}).data
            elif validated_data.get('status') == OpdAppointment.RESCHEDULED_PATIENT:
                if validated_data.get("start_date") and validated_data.get('start_time'):
                    time_slot_start = utils.form_time_slot(
                        validated_data.get("start_date"),
                        validated_data.get("start_time"))
                    if opd_appointment.time_slot_start == time_slot_start:
                        resp = {
                            "status": 0,
                            "message": "Cannot Reschedule for same timeslot"
                        }
                        return resp

                    doctor_hospital = DoctorClinicTiming.objects.filter(doctor_clinic__doctor__is_live=True,
                                                                        doctor_clinic__hospital__is_live=True,
                                                                        doctor_clinic__doctor=opd_appointment.doctor,
                                                                        doctor_clinic__hospital=opd_appointment.hospital,
                                                                        day=time_slot_start.weekday(),
                                                                        start__lte=time_slot_start.hour,
                                                                        end__gte=time_slot_start.hour).first()
                    if doctor_hospital:
                        if opd_appointment.payment_type == OpdAppointment.INSURANCE and opd_appointment.insurance_id is not None:
                            user_insurance = UserInsurance.objects.get(id=opd_appointment.insurance_id)
                            if user_insurance:
                                insurance_threshold = user_insurance.insurance_plan.threshold.filter().first()
                                if doctor_hospital.mrp > insurance_threshold.opd_amount_limit or not user_insurance.is_valid():
                                    resp = {
                                        "status": 0,
                                        "message": "Appointment amount is not covered under insurance"
                                    }
                                    return resp
                                if time_slot_start > user_insurance.expiry_date or not user_insurance.is_valid():
                                    resp = {
                                        "status": 0,
                                        "message": "Appointment time is not covered under insurance"
                                    }
                                    return resp
                        if opd_appointment.payment_type in [OpdAppointment.VIP, OpdAppointment.GOLD] and opd_appointment.plus_plan is not None:
                            plus_user = PlusUser.objects.filter(id=opd_appointment.plus_plan_id).first()
                            if plus_user and time_slot_start > plus_user.expire_date:
                                resp = {
                                    "status": 0,
                                    "message": "Appointment time is not covered under Gold"
                                }
                                return resp




                        old_deal_price = opd_appointment.deal_price
                        old_effective_price = opd_appointment.effective_price
                        coupon_discount = opd_appointment.discount
                        if coupon_discount > doctor_hospital.deal_price:
                            new_effective_price = 0
                        else:
                            if opd_appointment.insurance_id is None and opd_appointment.plus_plan_id is None:
                                new_effective_price = doctor_hospital.deal_price - coupon_discount
                            elif opd_appointment.plus_plan_id is not None:
                                plus_user = opd_appointment.user.active_plus_user
                                price_data = {"mrp": doctor_hospital.mrp, "deal_price": doctor_hospital.deal_price,
                                              "cod_deal_price": doctor_hospital.cod_deal_price,
                                              "fees": doctor_hospital.fees}
                                if plus_user:
                                    new_effective_price, convenience_charge = self.get_plus_user_effective_price(
                                        plus_user, price_data, "DOCTOR")
                                    if opd_appointment.plus_plan.plan.is_gold:
                                        order_obj = Order.objects.filter(reference_id=opd_appointment.id).first()
                                        action_data = order_obj.action_data
                                        if action_data:
                                            discount = int(action_data.get('discount', 0))
                                            if discount and discount > 0:
                                                new_effective_price = (new_effective_price + convenience_charge) - discount
                                            else:
                                                new_effective_price = new_effective_price + convenience_charge
                                        else:
                                            new_effective_price = new_effective_price + convenience_charge
                                    else:
                                        new_effective_price = old_effective_price
                            else:
                                new_effective_price = 0.0
                        if opd_appointment.procedures.count():
                            doctor_details = opd_appointment.get_procedures()[0]
                            old_agreed_price = Decimal(doctor_details["agreed_price"])
                            new_fees = opd_appointment.fees - old_agreed_price + doctor_hospital.fees
                            new_deal_price = opd_appointment.deal_price
                            new_mrp = opd_appointment.mrp
                            new_effective_price = opd_appointment.effective_price
                        else:
                            new_fees = doctor_hospital.fees
                            new_deal_price = doctor_hospital.deal_price
                            new_mrp = doctor_hospital.mrp

                        new_appointment = {
                            "id": opd_appointment.id,
                            "doctor": opd_appointment.doctor,
                            "hospital": opd_appointment.hospital,
                            "profile": opd_appointment.profile,
                            "profile_detail": opd_appointment.profile_detail,
                            "user": opd_appointment.user,

                            "booked_by": opd_appointment.booked_by,
                            "fees": new_fees,
                            "deal_price": new_deal_price,
                            "effective_price": new_effective_price,
                            "mrp": new_mrp,
                            "time_slot_start": time_slot_start,
                            "payment_type": opd_appointment.payment_type,
                            "discount": coupon_discount
                        }
                        resp = self.extract_payment_details(request, opd_appointment, new_appointment,
                                                            account_models.Order.DOCTOR_PRODUCT_ID)
                    else:
                        resp = {
                            "status": 0,
                            "message": "No time slot available for the give day and time."
                        }

            if validated_data['status'] == OpdAppointment.COMPLETED:
                opd_appointment.action_completed()
                resp = AppointmentRetrieveSerializer(opd_appointment, context={"request": request}).data
            return resp

    def get_appointment_coupon_price(self, discounted_price, effective_price):
        coupon_price = discounted_price - effective_price
        return coupon_price

    @transaction.atomic
    def extract_payment_details(self, request, appointment_details, new_appointment_details, product_id):
        resp = dict()
        user = request.user

        if appointment_details.payment_type == OpdAppointment.PREPAID and isinstance(appointment_details,OpdAppointment) and not appointment_details.procedures.count():
            remaining_amount = 0
            consumer_account = account_models.ConsumerAccount.objects.get_or_create(user=user)
            consumer_account = account_models.ConsumerAccount.objects.select_for_update().get(user=user)
            balance = consumer_account.balance

            resp["is_agent"] = False
            if hasattr(request, 'agent') and request.agent:
                resp["is_agent"] = True
                balance = 0

            if balance + appointment_details.effective_price >= new_appointment_details.get('effective_price'):
                # Debit or Refund/Credit in Account
                if appointment_details.effective_price > new_appointment_details.get('effective_price'):
                    # TODO PM - Refund difference b/w effective price
                    consumer_account.credit_schedule(appointment_details, product_id, appointment_details.effective_price - new_appointment_details.get('effective_price'))
                    # consumer_account.credit_schedule(user_account_data, appointment_details.effective_price - new_appointment_details.get('effective_price'))
                else:
                    debit_balance = new_appointment_details.get('effective_price') - appointment_details.effective_price
                    if debit_balance:
                        consumer_account.debit_schedule(appointment_details, product_id, debit_balance)
                        # consumer_account.debit_schedule(user_account_data, debit_balance)

                # Update appointment
                if product_id == account_models.Order.DOCTOR_PRODUCT_ID:
                    appointment_details.action_rescheduled_patient(new_appointment_details)
                    appointment_serializer = AppointmentRetrieveSerializer(appointment_details, context={"request": request})
                if product_id == account_models.Order.LAB_PRODUCT_ID:
                    appointment_details.action_rescheduled_patient(new_appointment_details)
                    appointment_serializer = LabAppointmentRetrieveSerializer(appointment_details, context={"request": request})
                resp['status'] = 1
                resp['data'] = appointment_serializer.data
                resp['payment_required'] = False
                return resp
            else:
                current_balance = consumer_account.balance + appointment_details.effective_price
                new_appointment_details['time_slot_start'] = str(new_appointment_details['time_slot_start'])
                action = ''
                temp_app_details = copy.deepcopy(new_appointment_details)

                if product_id == account_models.Order.DOCTOR_PRODUCT_ID:
                    action = account_models.Order.OPD_APPOINTMENT_RESCHEDULE
                    opdappointment_transform(temp_app_details)
                elif product_id == account_models.Order.LAB_PRODUCT_ID:
                    action = Order.LAB_APPOINTMENT_RESCHEDULE
                    labappointment_transform(temp_app_details)

                order = account_models.Order.objects.create(
                    product_id=product_id,
                    action=action,
                    action_data=temp_app_details,
                    amount=new_appointment_details.get('effective_price') - current_balance,
                    wallet_amount=current_balance,
                    # reference_id=appointment_details.id,
                    payment_status=account_models.Order.PAYMENT_PENDING
                )
                new_appointment_details["payable_amount"] = new_appointment_details.get('effective_price') - balance
                resp['status'] = 1
                resp['data'], resp['payment_required'] = self.payment_details(request, new_appointment_details, product_id, order.id)
                return resp
        else:
            if product_id == account_models.Order.DOCTOR_PRODUCT_ID:
                appointment_details.action_rescheduled_patient(new_appointment_details)
                appointment_serializer = AppointmentRetrieveSerializer(appointment_details,
                                                                       context={"request": request})
            if product_id == account_models.Order.LAB_PRODUCT_ID:
                appointment_details.action_rescheduled_patient(new_appointment_details)
                appointment_serializer = LabAppointmentRetrieveSerializer(appointment_details,
                                                                          context={"request": request})
            resp['status'] = 1
            resp['data'] = appointment_serializer.data
            resp['payment_required'] = False
            return resp

    def payment_details(self, request, appointment_details, product_id, order_id):
        payment_required = True
        pgdata = dict()
        user = request.user
        user_profile = user.profiles.filter(is_default_user=True).first()
        pgdata['custId'] = user.id
        pgdata['mobile'] = user.phone_number
        pgdata['email'] = user.email
        if not user.email:
            pgdata['email'] = "dummy_appointment@docprime.com"

        pgdata['productId'] = product_id
        base_url = "https://{}".format(request.get_host())
        pgdata['surl'] = base_url + '/api/v1/user/transaction/save'
        pgdata['furl'] = base_url + '/api/v1/user/transaction/save'
        pgdata['appointmentId'] = appointment_details.get('id')
        pgdata['orderId'] = order_id
        if user_profile:
            pgdata['name'] = user_profile.name
        else:
            pgdata['name'] = "DummyName"
        pgdata['txAmount'] = str(appointment_details['payable_amount'])

        secret_key = client_key = ""
        if product_id == Order.DOCTOR_PRODUCT_ID:
            secret_key = settings.PG_SECRET_KEY_P1
            client_key = settings.PG_CLIENT_KEY_P1
        elif product_id == Order.LAB_PRODUCT_ID:
            secret_key = settings.PG_SECRET_KEY_P2
            client_key = settings.PG_CLIENT_KEY_P2

        pgdata['hash'] = PgTransaction.create_pg_hash(pgdata, secret_key, client_key)

        return pgdata, payment_required

    def lab_appointment_list(self, request, params):
        user = request.user
        queryset = LabAppointment.objects.select_related('lab', 'profile', 'user')\
                                        .prefetch_related('lab__lab_image', 'lab__lab_documents', 'reports', 'test_mappings').filter(user=user)
        if queryset and params.get('profile_id'):
            queryset = queryset.filter(profile=params['profile_id'])
        range = params.get('range')
        # below code is not being used; Sorting will be done in parent method
        # if range and range == 'upcoming':
        #     queryset = queryset.filter(time_slot_start__gte=timezone.now(),
        #                                status__in=LabAppointment.ACTIVE_APPOINTMENT_STATUS).order_by('time_slot_start')
        # else:
        #     queryset = queryset.order_by('-time_slot_start')
        queryset = paginate_queryset(queryset, request, 100)
        serializer = LabAppointmentModelSerializer(queryset, many=True, context={"request": request})
        return serializer

    def doctor_appointment_list(self, request, params):
        user = request.user
        queryset = OpdAppointment.objects.select_related('profile', 'doctor', 'hospital', 'user').prefetch_related('doctor__images').filter(user=user)

        if not queryset:
            return Response([])
        serializer = AppointmentFilterUserSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        range = serializer.validated_data.get('range')
        hospital = serializer.validated_data.get('hospital_id')
        profile = serializer.validated_data.get('profile_id')

        if profile:
            queryset = queryset.filter(profile=profile)

        if hospital:
            queryset = queryset.filter(hospital=hospital)

        if range == 'previous':
            queryset = queryset.filter(time_slot_start__lte=timezone.now()).order_by('-time_slot_start')
        elif range == 'upcoming':
            queryset = queryset.filter(
                status__in=OpdAppointment.ACTIVE_APPOINTMENT_STATUS,
                time_slot_start__gt=timezone.now()).order_by('time_slot_start')
        elif range == 'pending':
            queryset = queryset.filter(time_slot_start__gt=timezone.now(),
                                       status=OpdAppointment.CREATED).order_by('time_slot_start')
        else:
            queryset = queryset.order_by('-time_slot_start')

        queryset = paginate_queryset(queryset, request, 100)
        serializer = OpdAppointmentSerializer(queryset, many=True,context={"request": request})
        return serializer



class AddressViewsSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        request = self.request
        return Address.objects.filter(user=request.user).order_by('address')

    def create(self, request, *args, **kwargs):
        data = request.data

        serializer = serializers.AddressSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        loc_position = utils.get_location(data.get('locality_location_lat'), data.get('locality_location_long'))
        land_position = utils.get_location(data.get('landmark_location_lat'), data.get('landmark_location_long'))
        address = None
        if land_position is None:
            if not Address.objects.filter(user=request.user).filter(**validated_data).filter(
                    locality_location__distance_lte=(loc_position, 0)).exists():
                validated_data["locality_location"] = loc_position
                validated_data["landmark_location"] = land_position
                validated_data['user'] = request.user
                address = Address.objects.create(**validated_data)
        else:
            if not Address.objects.filter(user=request.user).filter(**validated_data).filter(
                    locality_location__distance_lte=(loc_position, 0),
                    landmark_location__distance_lte=(land_position, 0)).exists() and not address:
                validated_data["locality_location"] = loc_position
                validated_data["landmark_location"] = land_position
                validated_data['user'] = request.user
                address = Address.objects.create(**validated_data)
        if not address:
            if land_position is None:
                address = Address.objects.filter(user=request.user).filter(**validated_data).filter(
                    locality_location__distance_lte=(loc_position, 0)).first()
            else:
                address = Address.objects.filter(user=request.user).filter(**validated_data).filter(
                    locality_location__distance_lte=(loc_position, 0),
                    landmark_location__distance_lte=(land_position, 0)).first()
        serializer = serializers.AddressSerializer(address)
        return Response(serializer.data)

    def update(self, request, pk=None):
        data = {key: value for key, value in request.data.items()}
        validated_data = dict()
        if data.get('locality_location_lat') and data.get('locality_location_long'):
            validated_data["locality_location"] = utils.get_location(data.get('locality_location_lat'), data.get('locality_location_long'))
        if data.get('landmark_location_lat') and data.get('landmark_location_long'):
            validated_data["landmark_location"] = utils.get_location(data.get('landmark_location_lat'), data.get('landmark_location_long'))
        data['user'] = request.user.id
        address = self.get_queryset().filter(pk=pk)
        if data.get("is_default"):
            add_default_qs = Address.objects.filter(user=request.user.id, is_default=True)
            if add_default_qs:
                add_default_qs.update(is_default=False)
        serializer = serializers.AddressSerializer(address.first(), data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        validated_data.update(serializer.validated_data)
        if address:
            address.update(**validated_data)
            address = address.first()
        else:
            validated_data["user"] = request.user
            address = Address.objects.create(**validated_data)
        resp_serializer = serializers.AddressSerializer(address)
        return Response(resp_serializer.data)

    def destroy(self, request, pk=None):
        address = get_object_or_404(Address, pk=pk)
        is_default_address = address.is_default

        address.delete()

        if is_default_address:
            temp_addr = Address.objects.filter(user=request.user.id).first()
            if temp_addr:
                temp_addr.is_default = True
                temp_addr.save()
        return Response({
            "status": 1
        })


class AppointmentTransactionViewSet(viewsets.GenericViewSet):

    serializer_class = None
    queryset = AppointmentTransaction.objects.none()

    def save(self, request):
        LAB_REDIRECT_URL = request.build_absolute_uri("/") + "lab/appointment/{}"
        OPD_REDIRECT_URL = request.build_absolute_uri("/") + "opd/appointment/{}"
        data = request.data

        coded_response = data.get("response")
        if isinstance(coded_response, list):
            coded_response = coded_response[0]
        coded_response += "=="
        decoded_response = base64.b64decode(coded_response).decode()
        response = json.loads(decoded_response)
        transaction_time = parse(response.get("txDate"))
        AppointmentTransaction.objects.create(appointment=response.get("appointmentId"),
                                              transaction_time=transaction_time,
                                              transaction_status=response.get("txStatus"),
                                              status_code=response.get("statusCode"),
                                              transaction_details=response)
        if response.get("statusCode") == 1 and response.get("productId") == 1:
            opd_appointment = OpdAppointment.objects.filter(pk=response.get("appointmentId")).first()
            if opd_appointment:
                otp = random.randint(1000, 9999)
                opd_appointment.payment_status = OpdAppointment.PAYMENT_ACCEPTED
                opd_appointment.status = OpdAppointment.BOOKED
                opd_appointment.otp = otp
                opd_appointment.save()
        elif response.get("statusCode") == 1 and response.get("productId") == 2:
            lab_appointment = LabAppointment.objects.filter(pk=response.get("appointmentId")).first()
            if lab_appointment:
                otp = random.randint(1000, 9999)
                lab_appointment.payment_status = OpdAppointment.PAYMENT_ACCEPTED
                lab_appointment.status = LabAppointment.BOOKED
                lab_appointment.otp = otp
                lab_appointment.save()
        if response.get("productId") == 2:
            REDIRECT_URL = LAB_REDIRECT_URL.format(response.get("appointmentId"))
        else:
            REDIRECT_URL = OPD_REDIRECT_URL.format(response.get("appointmentId"))
        return HttpResponseRedirect(redirect_to=REDIRECT_URL)


class UserIDViewSet(viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @transaction.non_atomic_requests
    def retrieve(self, request):
        data = {
            "user_id": request.user.id
        }
        return Response(data)


class TransactionViewSet(viewsets.GenericViewSet):

    serializer_class = serializers.TransactionSerializer
    queryset = PgTransaction.objects.none()

    @transaction.atomic()
    def save(self, request):
        try:
            response = None
            coded_response = None
            data = request.data
            # Commenting below for testing
            try:
                coded_response = data.get("response")
                if isinstance(coded_response, list):
                    coded_response = coded_response[0]
                coded_response += "=="
                decoded_response = base64.b64decode(coded_response).decode()
                response = json.loads(decoded_response)
            except Exception as e:
                logger.error("Cannot decode pg data - " + str(e))

            try:
                pg_resp_code = int(response.get('statusCode'))
            except:
                logger.error("ValueError : statusCode is not type integer")
                pg_resp_code = None

            redirect_url = self.validate_post_transaction_response(request, response)
            return HttpResponseRedirect(redirect_to=redirect_url)
        except Exception as e:
            logger.error("Error - " + str(e))

    def validate_post_transaction_response(self, request, response):
        if response.get("orderId", None) and not response.get('items', None):
            redirect_url = self.validate_single_order_transaction(request, response)
        else:
            redirect_url = self.validate_multiple_order_transaction(request, response)
        return redirect_url

    def validate_single_order_transaction(self, request, response):
        base_url = settings.BASE_URL
        is_refund_process = False
        if request.query_params and request.query_params.get('sbig', False):
            base_url = settings.SBIG_BASE_URL

        ERROR_REDIRECT_URL = base_url + "/cart?error_code=1&error_message=%s"
        REDIRECT_URL = ERROR_REDIRECT_URL % "Error processing payment, please try again."
        SUCCESS_REDIRECT_URL = base_url + "/order/summary/%s"
        LAB_REDIRECT_URL = base_url + "/lab/appointment"
        OPD_REDIRECT_URL = base_url + "/opd/appointment"
        PLAN_REDIRECT_URL = base_url + "/prime/success?user_plan="
        ECONSULT_REDIRECT_URL = base_url + "/econsult?order_id=%s&payment=success"

        CHAT_ERROR_REDIRECT_URL = base_url + "/mobileviewchat?payment=fail&error_message=%s" % "Error processing payment, please try again."
        CHAT_REDIRECT_URL = CHAT_ERROR_REDIRECT_URL
        CHAT_SUCCESS_REDIRECT_URL = base_url + "/mobileviewchat?payment=success&order_id=%s&consultation_id=%s"
        PLUS_FAILURE_REDIRECT_URL = base_url + ""
        PLUS_SUCCESS_REDIRECT_URL = base_url + "/vip-club-activated-details?payment=success&id=%s"

        # log pg data
        try:
            pg_resp_code = int(response.get('statusCode'))
            args = {'order_id': response.get("orderId"), 'status_code': pg_resp_code, 'source': response.get("source")}
            status_type = PaymentProcessStatus.get_status_type(pg_resp_code, response.get('txStatus'))
            # PgLogs.objects.create(decoded_response=response, coded_response=coded_response)
            if settings.SAVE_LOGS:
                save_pg_response.apply_async(
                    (mongo_pglogs.TXN_RESPONSE, response.get("orderId"), None, response, None, response.get('customerId')),
                    eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
            save_payment_status.apply_async((status_type, args), eta=timezone.localtime(), )
        except Exception as e:
            logger.error("Cannot log pg response - " + str(e))

        # Check if already processes
        try:
            if response and response.get("orderNo"):
                # pg_txn = PgTransaction.objects.filter(order_no__iexact=response.get("orderNo")).first()
                pg_txn = PgTransaction.objects.filter(order_no__iexact=response.get("orderNo"), order__id=int(response.get('orderId'))).first()
                if pg_txn:
                    is_preauth = False
                    if pg_txn.is_preauth():
                        is_preauth = True
                        pg_txn.status_code = response.get('statusCode')
                        pg_txn.status_type = response.get('txStatus')
                        pg_txn.payment_mode = response.get("paymentMode")
                        pg_txn.bank_name = response.get('bankName')
                        pg_txn.transaction_id = response.get('pgTxId')
                        pg_txn.bank_id = response.get('bankTxId')
                        # pg_txn.payment_captured = True
                        pg_txn.save()

                        ctx_txn = ConsumerTransaction.objects.filter(order_id=pg_txn.order_id,
                                                                     action=ConsumerTransaction.PAYMENT).last()
                        ctx_txn.transaction_id = response.get('pgTxId')
                        ctx_txn.save()

                        if response.get('txStatus') in ['TXN_SUCCESS', 'TXN_RELEASE']:
                            send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no, 'capture'), countdown=1)
                    send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no,), countdown=1)
                    if pg_txn.product_id == Order.CHAT_PRODUCT_ID:
                        chat_order = Order.objects.filter(pk=pg_txn.order_id).first()
                        if chat_order:
                            CHAT_REDIRECT_URL = CHAT_SUCCESS_REDIRECT_URL % (chat_order.id, chat_order.reference_id)
                            json_url = '{"url": "%s"}' % CHAT_REDIRECT_URL
                            log_created_at = str(datetime.datetime.now())
                            if settings.SAVE_LOGS:
                                save_pg_response.apply_async((mongo_pglogs.RESPONSE_TO_CHAT, chat_order.id, None, json_url, None, None, log_created_at), eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
                        return CHAT_REDIRECT_URL
                    else:
                        REDIRECT_URL = (SUCCESS_REDIRECT_URL % pg_txn.order_id) + "?payment_success=true"
                        return REDIRECT_URL
        except Exception as e:
            logger.error("Error in sending pg acknowledge - " + str(e))

        # For testing only
        # response = request.data
        success_in_process = False
        processed_data = {}

        order_obj = Order.objects.select_for_update().filter(pk=response.get("orderId")).first()
        convert_cod_to_prepaid = False
        pg_response_amount = response.get('txAmount', None)
        if pg_response_amount:
            pg_response_amount = float(pg_response_amount)
        else:
            pg_response_amount = 0.0

        # try:
        #     if float(order_obj.amount) != pg_response_amount:
        #         send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),), countdown=1)
        #         return REDIRECT_URL
        # except Exception as e:
        #     logger.error("Error in sending pg acknowledge - after transaction amount mismatch " + str(e))

        try:
            # if order_obj and response and order_obj.is_cod_order and order_obj.get_deal_price_without_coupon <= Decimal(response.get('txAmount')):
            if order_obj and response and order_obj.is_cod_order and order_obj.amount <= Decimal(
                    response.get('txAmount')):
                convert_cod_to_prepaid = True
                order_obj.amount = Decimal(response.get('txAmount'))
                order_obj.save()
        except:
            pass

        if pg_resp_code == 1 and order_obj:
            # send ack for dummy_txn response
            # todo - ask pg-team to send flag for this to avoid amount condition check
            if response and response.get("txAmount") and int(Decimal(response.get("txAmount"))) == 0 \
                    and response.get('txStatus') == 'TXN_SUCCESS':
                send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),),
                                                countdown=1)
            else:
                if response.get("couponUsed") and response.get("couponUsed") == "false":
                    order_obj.update_fields_after_coupon_remove()

                response_data = None
                resp_serializer = serializers.TransactionSerializer(data=response)
                if resp_serializer.is_valid():
                    response_data = self.form_pg_transaction_data(resp_serializer.validated_data, order_obj)

                    # For Testing
                    if PgTransaction.is_valid_hash(response, product_id=order_obj.product_id):
                        pg_tx_queryset = None
                        # if True:
                        try:
                            with transaction.atomic():
                                pg_tx_queryset = PgTransaction.objects.create(**response_data)
                                if float(order_obj.amount) != pg_response_amount:
                                    is_refund_process = True
                        except Exception as e:
                            logger.error("Error in saving PG Transaction Data - " + str(e))

                        if not is_refund_process:
                            try:
                                with transaction.atomic():
                                    processed_data = order_obj.process_pg_order(convert_cod_to_prepaid)
                                    success_in_process = True
                            except Exception as e:
                                logger.error("Error in processing order - " + str(e))
                        else:
                            consumer_account = ConsumerAccount.objects.get_or_create(user=order_obj.user)
                            consumer_account = ConsumerAccount.objects.select_for_update().get(user=order_obj.user)
                            ctx_objs = consumer_account.debit_refund()
                            if ctx_objs:
                                for ctx_obj in ctx_objs:
                                    ConsumerRefund.initiate_refund(ctx_obj.user, ctx_obj)
                            send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),),
                                                            countdown=1)
                            return REDIRECT_URL
                else:
                    logger.error("Invalid pg data - " + json.dumps(resp_serializer.errors))
        elif order_obj:
            # send acknowledge if status is TXN_FAILURE to stop callbacks from pg. Do not send acknowledgement if no entry in pg.
            try:
                if response and response.get("orderNo") and response.get("orderId") and response.get(
                        'txStatus'):
                    if response.get('txStatus') == 'TXN_FAILURE':
                        send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),), countdown=1)
                    if response.get('txStatus') == 'TXN_PENDING' and pg_resp_code == 5:
                        send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),), countdown=1)
            except Exception as e:
                logger.error("Error in sending pg acknowledge - " + str(e))

            try:
                has_changed = order_obj.change_payment_status(Order.PAYMENT_FAILURE)
                if has_changed:
                    self.send_failure_ops_email(order_obj)
            except Exception as e:
                logger.error("Error sending payment failure email - " + str(e))

        if success_in_process:
            if processed_data.get("type") == "all":
                REDIRECT_URL = (SUCCESS_REDIRECT_URL % order_obj.id) + "?payment_success=true"
            elif processed_data.get("type") == "doctor":
                REDIRECT_URL = OPD_REDIRECT_URL + "/" + str(processed_data.get("id", "")) + "?payment_success=true"
            elif processed_data.get("type") == "lab":
                REDIRECT_URL = LAB_REDIRECT_URL + "/" + str(processed_data.get("id", "")) + "?payment_success=true"
            elif processed_data.get("type") == "insurance":
                REDIRECT_URL = settings.BASE_URL + "/insurance/complete?payment_success=true&id=" + str(
                    processed_data.get("id", ""))
            elif processed_data.get("type") == "plan":
                REDIRECT_URL = PLAN_REDIRECT_URL + str(processed_data.get("id", "")) + "&payment_success=true"
            elif processed_data.get("type") == "econsultation":
                REDIRECT_URL = ECONSULT_REDIRECT_URL % order_obj.id
            elif processed_data.get('type') == "chat":
                CHAT_REDIRECT_URL = CHAT_SUCCESS_REDIRECT_URL % (order_obj.id, str(processed_data.get("id", "")))
            elif processed_data.get('type') == "plus":
                REDIRECT_URL = PLUS_SUCCESS_REDIRECT_URL % str(processed_data.get("id", ""))

        try:
            if response and response.get("orderNo"):
                pg_txn = PgTransaction.objects.filter(order_no__iexact=response.get("orderNo")).first()
                if pg_txn:
                    send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no,), countdown=1)
        except Exception as e:
            logger.error("Error in sending pg acknowledge - " + str(e))

        if order_obj.product_id == Order.CHAT_PRODUCT_ID:
            json_url = '{"url": "%s"}' % CHAT_REDIRECT_URL
            log_created_at = str(datetime.datetime.now())
            if settings.SAVE_LOGS:
                save_pg_response.apply_async(
                    (mongo_pglogs.RESPONSE_TO_CHAT, order_obj.id, None, json_url, None, None, log_created_at),
                    eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
            return CHAT_REDIRECT_URL
        return REDIRECT_URL

    def validate_multiple_order_transaction(self, request, response):
        base_url = settings.BASE_URL
        is_refund_process = False
        if request.query_params and request.query_params.get('sbig', False):
            base_url = settings.SBIG_BASE_URL

        ERROR_REDIRECT_URL = base_url + "/cart?error_code=1&error_message=%s"
        REDIRECT_URL = ERROR_REDIRECT_URL % "Error processing payment, please try again."
        SUCCESS_REDIRECT_URL = base_url + "/order/summary/%s"
        LAB_REDIRECT_URL = base_url + "/lab/appointment"
        OPD_REDIRECT_URL = base_url + "/opd/appointment"
        PLAN_REDIRECT_URL = base_url + "/prime/success?user_plan="
        ECONSULT_REDIRECT_URL = base_url + "/econsult?order_id=%s&payment=success"

        CHAT_ERROR_REDIRECT_URL = base_url + "/mobileviewchat?payment=fail&error_message=%s" % "Error processing payment, please try again."
        CHAT_REDIRECT_URL = CHAT_ERROR_REDIRECT_URL
        CHAT_SUCCESS_REDIRECT_URL = base_url + "/mobileviewchat?payment=success&order_id=%s&consultation_id=%s"
        PLUS_FAILURE_REDIRECT_URL = base_url + ""
        PLUS_SUCCESS_REDIRECT_URL = base_url + "/vip-club-activated-details?payment=success&id=%s"

        pg_resp_code = int(response.get('statusCode'))
        # items = response.get('items' ,[]).sort(key='productId', reverse=True)

        items = copy.deepcopy(response.get('items', []))
        if len(items) == 1 and int(items[0].get('productId')) == Order.GOLD_PRODUCT_ID:
            gold_order_id = int(items[0].get('orderId'))
            if gold_order_id:
                sibling_order = Order.objects.filter(single_booking_id=gold_order_id).first()
                if sibling_order:
                    items.append({'productId': sibling_order.product_id, 'orderId': sibling_order.id, 'txAmount': 0})

        items = sorted(items, key=lambda x: int(x['productId']), reverse=True)
        for item in items:
            try:
                item['productId'] = int(item['productId'])
                order_id = item.get('orderId', None)
                product_id = item.get('productId', None)
                amount = item.get('txAmount', None)
                pg_response_amount = amount
                if pg_response_amount:
                    pg_response_amount = float(pg_response_amount)
                else:
                    pg_response_amount = 0.0
                # log pg data
                try:
                    args = {'order_id': order_id, 'status_code': pg_resp_code, 'source': response.get("source")}
                    status_type = PaymentProcessStatus.get_status_type(pg_resp_code, response.get('txStatus'))

                    # PgLogs.objects.create(decoded_response=response, coded_response=coded_response)
                    if settings.SAVE_LOGS:
                        save_pg_response.apply_async((mongo_pglogs.TXN_RESPONSE, order_id, None, response, None, response.get('customerId')), eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
                    save_payment_status.apply_async((status_type, args), eta=timezone.localtime(),)
                except Exception as e:
                    logger.error("Cannot log pg response - " + str(e))

                # Check if already processes
                try:
                    if response and response.get("orderNo"):
                        pg_txn = PgTransaction.objects.filter(order_no__iexact=response.get("orderNo"), order__id=int(item.get('orderId'))).first()
                        if pg_txn:
                            is_preauth = False
                            if pg_txn.is_preauth():
                                is_preauth = True
                                pg_txn.status_code = response.get('statusCode')
                                pg_txn.status_type = response.get('txStatus')
                                pg_txn.payment_mode = response.get("paymentMode")
                                pg_txn.bank_name = response.get('bankName')
                                pg_txn.transaction_id = response.get('pgTxId')
                                pg_txn.bank_id = response.get('bankTxId')
                                #pg_txn.payment_captured = True
                                pg_txn.save()

                                ctx_txn = ConsumerTransaction.objects.filter(order_id=pg_txn.order_id,
                                                                             action=ConsumerTransaction.PAYMENT).last()
                                ctx_txn.transaction_id = response.get('pgTxId')
                                ctx_txn.save()

                                if response.get('txStatus') in ['TXN_SUCCESS', 'TXN_RELEASE']:
                                    send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no, 'capture'), countdown=1)
                            send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no,), countdown=1)
                            if pg_txn.product_id == Order.CHAT_PRODUCT_ID:
                                chat_order = Order.objects.filter(pk=pg_txn.order_id).first()
                                if chat_order:
                                    CHAT_REDIRECT_URL = CHAT_SUCCESS_REDIRECT_URL % (chat_order.id, chat_order.reference_id)
                                return CHAT_REDIRECT_URL
                            else:
                                REDIRECT_URL = (SUCCESS_REDIRECT_URL % pg_txn.order_id) + "?payment_success=true"
                                return REDIRECT_URL
                except Exception as e:
                    logger.error("Error in sending pg acknowledge - " + str(e))


                # For testing only
                # response = request.data
                success_in_process = False
                processed_data = {}

                order_obj = Order.objects.select_for_update().filter(pk=order_id).first()
                convert_cod_to_prepaid = False

                # try:
                #     if float(order_obj.amount) != pg_response_amount:
                #         send_pg_acknowledge.apply_async((order_id, response.get("orderNo"),), countdown=1)
                #         return REDIRECT_URL
                # except Exception as e:
                #     logger.error("Error in sending pg acknowledge - after transaction amount mismatch" + str(e))

                try:
                    # if order_obj and response and order_obj.is_cod_order and order_obj.get_deal_price_without_coupon <= Decimal(response.get('txAmount')):
                    if order_obj and response and order_obj.is_cod_order and order_obj.amount <= Decimal(amount):
                        convert_cod_to_prepaid = True
                        order_obj.amount = Decimal(amount)
                        order_obj.save()
                except:
                    pass

                if pg_resp_code == 1 and order_obj:
                    # send ack for dummy_txn response
                    # todo - ask pg-team to send flag for this to avoid amount condition check
                    if response and response.get("txAmount") and int(Decimal(response.get("txAmount"))) == 0 \
                            and response.get('txStatus') == 'TXN_SUCCESS':
                        send_pg_acknowledge.apply_async((response.get("orderId"), response.get("orderNo"),),
                                                        countdown=1)
                    else:
                        if response.get("couponUsed") and response.get("couponUsed") == "false":
                            order_obj.update_fields_after_coupon_remove()

                        response_data = None

                        if "items" in response:
                            virtual_response = copy.deepcopy(response)
                            del virtual_response['items']
                            virtual_response['orderId'] = item['orderId']
                            virtual_response['txAmount'] = item['txAmount']

                        resp_serializer = serializers.TransactionSerializer(data=virtual_response)

                        if resp_serializer.is_valid():
                            response_data = self.form_pg_transaction_data(resp_serializer.validated_data, order_obj)
                            # For Testing

                            if not order_obj.amount or order_obj.amount <= 0:
                                try:
                                    with transaction.atomic():
                                        processed_data = order_obj.process_pg_order(convert_cod_to_prepaid)
                                        success_in_process = True
                                except Exception as e:
                                    logger.error("Error in processing order - " + str(e))
                            else:
                                # Simplify the response for multiorder for ease of incomming checksum creation
                                order_items = sorted(response.get('items', []), key=lambda x: int(x['orderId']))
                                stringify_item = '['
                                if order_items.__class__.__name__ == 'list':
                                    for i in order_items:
                                        stringify_item = stringify_item + '{'
                                        if i.__class__.__name__ == 'dict':
                                            for k in sorted(i.keys()):
                                                stringify_item = stringify_item + k + '=' + str(i[k]) + ';'

                                        stringify_item = stringify_item + '};'

                                    if stringify_item[-1:] == ';':
                                        stringify_item = stringify_item[:-1]
                                    stringify_item = stringify_item + ']'

                                virtual_response['items'] = stringify_item
                                del virtual_response['orderId']
                                virtual_response.pop('txAmount', None)

                                if PgTransaction.is_valid_hash(virtual_response, product_id=order_obj.product_id):
                                    pg_tx_queryset = None
                                    # if True:
                                    try:
                                        with transaction.atomic():
                                            pg_tx_queryset = PgTransaction.objects.create(**response_data)
                                            if float(order_obj.amount) != pg_response_amount:
                                                is_refund_process = True
                                    except Exception as e:
                                        logger.error("Error in saving PG Transaction Data - " + str(e))

                                    if not is_refund_process:
                                        try:
                                            with transaction.atomic():
                                                processed_data = order_obj.process_pg_order(convert_cod_to_prepaid)
                                                success_in_process = True
                                        except Exception as e:
                                            logger.error("Error in processing order - " + str(e))
                                    else:
                                        consumer_account = ConsumerAccount.objects.get_or_create(user=order_obj.user)
                                        consumer_account = ConsumerAccount.objects.select_for_update().get(
                                            user=order_obj.user)
                                        ctx_objs = consumer_account.debit_refund()
                                        if ctx_objs:
                                            for ctx_obj in ctx_objs:
                                                ConsumerRefund.initiate_refund(ctx_obj.user, ctx_obj)
                                        send_pg_acknowledge.apply_async(
                                            (response.get("orderId"), response.get("orderNo"),),
                                            countdown=1)
                                        return REDIRECT_URL

                        else:
                            logger.error("Invalid pg data - " + json.dumps(resp_serializer.errors))
                elif order_obj:
                    # send acknowledge if status is TXN_FAILURE to stop callbacks from pg. Do not send acknowledgement if no entry in pg.
                    try:
                        if response and response.get("orderNo") and order_id and response.get(
                                'txStatus') and response.get('txStatus') == 'TXN_FAILURE':
                            send_pg_acknowledge.apply_async((order_id, response.get("orderNo"),), countdown=1)
                        if response and response.get("orderNo") and response.get("orderId") and response.get(
                                'txStatus') and response.get('txStatus') == 'TXN_SUCCESS' and pg_resp_code == 5:
                            send_pg_acknowledge.apply_async((int(item.get('orderId')), response.get("orderNo"),),
                                                            countdown=1)
                    except Exception as e:
                        logger.error("Error in sending pg acknowledge - " + str(e))

                    try:
                        has_changed = order_obj.change_payment_status(Order.PAYMENT_FAILURE)
                        if has_changed:
                            self.send_failure_ops_email(order_obj)
                    except Exception as e:
                        logger.error("Error sending payment failure email - " + str(e))

                if success_in_process:
                    if processed_data.get("type") == "all":
                        REDIRECT_URL = (SUCCESS_REDIRECT_URL % order_obj.id) + "?payment_success=true"
                    elif processed_data.get("type") == "doctor":
                        REDIRECT_URL = OPD_REDIRECT_URL + "/" + str(processed_data.get("id", "")) + "?payment_success=true"
                    elif processed_data.get("type") == "lab":
                        REDIRECT_URL = LAB_REDIRECT_URL + "/" + str(processed_data.get("id","")) + "?payment_success=true"
                    elif processed_data.get("type") == "insurance":
                        REDIRECT_URL = settings.BASE_URL + "/insurance/complete?payment_success=true&id=" + str(processed_data.get("id", ""))
                    elif processed_data.get("type") == "plan":
                        REDIRECT_URL = PLAN_REDIRECT_URL + str(processed_data.get("id", "")) + "&payment_success=true"
                    elif processed_data.get("type") == "econsultation":
                        REDIRECT_URL = ECONSULT_REDIRECT_URL % order_obj.id
                    elif processed_data.get('type') == "chat":
                        CHAT_REDIRECT_URL = CHAT_SUCCESS_REDIRECT_URL % (order_obj.id, str(processed_data.get("id", "")))
                    elif processed_data.get('type') == "plus":
                        REDIRECT_URL = PLUS_SUCCESS_REDIRECT_URL % str(processed_data.get("id", ""))
            except Exception as e:
                logger.error("Error - " + str(e))

            try:
                if response and response.get("orderNo"):
                    pg_txn = PgTransaction.objects.filter(order_no__iexact=response.get("orderNo"), order__id=int(item.get('orderId'))).first()
                    if pg_txn:
                        send_pg_acknowledge.apply_async((pg_txn.order_id, pg_txn.order_no,), countdown=1)
            except Exception as e:
                logger.error("Error in sending pg acknowledge - " + str(e))

        return REDIRECT_URL

    def form_pg_transaction_data(self, response, order_obj):
        from keel.api.v1.utils import format_return_value
        data = dict()
        user_id = order_obj.get_user_id()
        user = get_object_or_404(User, pk=user_id)
        data['user'] = user
        data['product_id'] = order_obj.product_id
        data['order_no'] = response.get('orderNo')
        data['order_id'] = order_obj.id
        data['reference_id'] = order_obj.reference_id
        data['type'] = PgTransaction.CREDIT
        # data['amount'] = order_obj.amount
        data['amount'] = response.get('txAmount')
        data['payment_mode'] = format_return_value(response.get('paymentMode'))
        data['response_code'] = response.get('responseCode')
        data['bank_id'] = format_return_value(response.get('bankTxId'))
        transaction_time = parse(response.get("txDate"))
        data['transaction_date'] = transaction_time
        data['bank_name'] = format_return_value(response.get('bankName'))
        data['currency'] = response.get('currency')
        data['status_code'] = response.get('statusCode')
        data['pg_name'] = format_return_value(response.get('pgGatewayName'))
        data['status_type'] = response.get('txStatus')
        data['transaction_id'] = format_return_value(response.get('pgTxId'))
        data['pb_gateway_name'] = response.get('pbGatewayName')
        data['nodal_id'] = response.get('nodalId')
        # if order_obj.product_id == Order.INSURANCE_PRODUCT_ID:
        #     data['nodal_id'] = PgTransaction.NODAL2
        # else:
        #     data['nodal_id'] = PgTransaction.NODAL1

        return data

    @transaction.atomic
    def block_schedule_transaction(self, data):
        consumer_account = ConsumerAccount.objects.get_or_create(user=data["user"])
        consumer_account = ConsumerAccount.objects.select_for_update().get(user=data["user"])

        appointment_amount, obj = self.get_appointment_amount(data)

        if consumer_account.balance < appointment_amount:
            return appointment_amount - consumer_account.balance
        else:
            obj.confirm_appointment(consumer_account, data, appointment_amount)

        return 0

    def get_appointment_amount(self, data):
        amount = 0
        if data["product"] == 2:
            obj = get_object_or_404(LabAppointment, pk=data['order'])
            amount = obj.price
        elif data["product"] == 1:
            obj = get_object_or_404(OpdAppointment, pk=data['order'])
            amount = obj.fees

        return amount, obj

    def send_failure_ops_email(self, order_obj):
        booking_type = "Insurance " if order_obj.product_id == Order.INSURANCE_PRODUCT_ID else ""
        html_body = "{}Payment failed for user with " \
                    "user id - {} and phone number - {}" \
                    ", order id - {}.".format(booking_type, order_obj.user.id, order_obj.user.phone_number, order_obj.id)

        # Push the order failure case to matrix.
        # push_order_to_matrix.apply_async(({'order_id': order_obj.id},), countdown=5)

        for email in settings.ORDER_FAILURE_EMAIL_ID:
            EmailNotification.publish_ops_email(email, html_body, 'Payment failure for order')


class UserTransactionViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserTransactionModelSerializer
    queryset = ConsumerTransaction.objects.all()
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)

    @transaction.non_atomic_requests
    @use_slave
    def list(self, request):
        user = request.user
        tx_queryset = ConsumerTransaction.objects.filter(user=user).order_by('-id')
        consumer_account = ConsumerAccount.objects.filter(user=user).first()

        tx_serializable_data = list()
        consumer_balance = 0
        consumer_cashback = 0
        if tx_queryset.exists():
            tx_queryset = paginate_queryset(tx_queryset, request)
            tx_serializer = serializers.UserTransactionModelSerializer(tx_queryset, many=True)
            tx_serializable_data = tx_serializer.data

        if consumer_account:
            consumer_balance = consumer_account.balance
            consumer_cashback = consumer_account.cashback

        resp = dict()
        resp["user_transactions"] = tx_serializable_data
        resp["user_wallet_balance"] = consumer_balance
        resp["consumer_cashback"] = consumer_cashback
        return Response(data=resp)


class ConsumerAccountViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = ConsumerAccount.objects.all()
    serializer_class = serializers.ConsumerAccountModelSerializer


class OrderHistoryViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsConsumer,)

    @transaction.non_atomic_requests
    def list(self, request):
        # opd_action_data = list()
        # lab_action_data = list()
        available_lab_test = list()
        order_action_list = list()
        doc_hosp_query = Q()

        for order in Order.objects.filter(action_data__user=request.user.id, is_viewable=True,
                                          payment_status=Order.PAYMENT_PENDING).order_by('-created_at')[:5]:
            action_data = order.action_data
            action_data["product_id"] = order.product_id
            if order.product_id == Order.DOCTOR_PRODUCT_ID:
                # opd_action_data.append(action_data)
                doc_hosp_query = doc_hosp_query | (Q(doctor=action_data.get("doctor"), hospital=action_data.get("hospital")))
            elif order.product_id == Order.LAB_PRODUCT_ID:
                # lab_action_data.append(action_data)
                available_lab_test.extend(action_data.get("lab_test"))
            order_action_list.append(action_data)

        doc_hosp_details = defaultdict(dict)
        if doc_hosp_query:
            doc_hosp_obj = DoctorClinic.objects.prefetch_related('doctor', 'hospital', 'doctor__images').filter(doc_hosp_query)
            for data in doc_hosp_obj:
                doc_hosp_details[data.hospital.id][data.doctor.id] = {
                    "doctor_name": data.doctor.name,
                    "hospital_name": data.hospital.name,
                    "doctor_thumbnail": request.build_absolute_uri(data.doctor.images.first().name.url) if data.doctor.images.all().first() else None
                }

        lab_name = dict()
        lab_test_map = dict()
        if available_lab_test:
            test_ids = AvailableLabTest.objects.prefetch_related('lab_pricing_group__labs', 'test').filter(pk__in=available_lab_test)
            lab_test_map = dict()
            for data in test_ids:
                for lab_data in data.lab_pricing_group.labs.all():
                    lab_name[lab_data.id] = {
                        'name': lab_data.name,
                        "lab_thumbnail": request.build_absolute_uri(lab_data.get_thumbnail()) if lab_data.get_thumbnail() else None
                    }
                lab_test_map[data.id] = {"id": data.test.id,
                                         "name": data.test.name
                                         }
        orders = []

        for action_data in order_action_list:
            if action_data["product_id"] == Order.DOCTOR_PRODUCT_ID:
                if action_data["hospital"] not in doc_hosp_details or action_data["doctor"] not in doc_hosp_details[action_data["hospital"]]:
                    continue
                data = {
                    "doctor": action_data.get("doctor"),
                    "doctor_name": doc_hosp_details[action_data["hospital"]][action_data["doctor"]]["doctor_name"],
                    "hospital": action_data.get("hospital"),
                    "hospital_name": doc_hosp_details[action_data["hospital"]][action_data["doctor"]]["hospital_name"],
                    "doctor_thumbnail": doc_hosp_details[action_data["hospital"]][action_data["doctor"]][
                        "doctor_thumbnail"],
                    "profile_detail": action_data.get("profile_detail"),
                    "profile": action_data.get("profile"),
                    "user": action_data.get("user"),
                    "time_slot_start": action_data.get("time_slot_start"),
                    "start_date": action_data.get("time_slot_start"),
                    "start_time": 0.0,  # not required here we are only validating fees
                    "payment_type": action_data.get("payment_type"),
                    "type": "opd"
                }
                data.pop("time_slot_start")
                data.pop("start_date")
                data.pop("start_time")
                orders.append(data)
            elif action_data["product_id"] == Order.LAB_PRODUCT_ID:
                if action_data['lab'] not in lab_name:
                    continue
                data = {
                    "lab": action_data.get("lab"),
                    "lab_name": lab_name[action_data['lab']]["name"],
                    "test_ids": [lab_test_map[x]["id"] for x in action_data.get("lab_test")],
                    "lab_thumbnail": lab_name[action_data['lab']]["lab_thumbnail"],
                    "profile": action_data.get("profile"),
                    "time_slot_start": action_data.get("time_slot_start"),
                    "start_date": action_data.get("time_slot_start"),
                    "start_time": 0.0,  # not required here we are only validating fees
                    "payment_type": action_data.get("payment_type"),
                    "type": "lab"
                }
                data.pop("time_slot_start")
                data.pop("start_date")
                data.pop("start_time")
                data["test_ids"] = [lab_test_map[x] for x in action_data.get("lab_test")]
                orders.append(data)
        return Response(orders)


class HospitalDoctorAppointmentPermissionViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsDoctor,)

    @transaction.non_atomic_requests
    def list(self, request):
        user = request.user
        manageable_hosp_list = GenericAdmin.get_manageable_hospitals(user)
        doc_hosp_queryset = (DoctorClinic.objects
                             .select_related('doctor', 'hospital')
                             .prefetch_related('doctor__manageable_doctors', 'hospital__manageable_hospitals',
                                               'hospital__partner_labs', 'hospital__partner_labs__lab')
                             .filter(Q(Q(doctor__is_live=True) | Q(doctor__source_type=Doctor.PROVIDER)),
                                     Q(Q(hospital__is_live=True) | Q(hospital__source_type=Hospital.PROVIDER)))
                             .annotate(doctor_gender=F('doctor__gender'),
                                       hospital_building=F('hospital__building'),
                                       hospital_name=F('hospital__name'),
                                       doctor_name=Case(
                                           When(doctor__name__istartswith='dr. ',
                                                then=Concat(Value('Dr. '), Substr(F('doctor__name'), 5))),
                                           When(doctor__name__istartswith='dr ',
                                                then=Concat(Value('Dr. '), Substr(F('doctor__name'), 4))),
                                           default=Concat(Value('Dr. '), F('doctor__name')),
                                       ),
                                       doctor_source_type=F('doctor__source_type'),
                                       doctor_is_live=F('doctor__is_live'),
                                       license=F('doctor__license'),
                                       is_license_verified=F('doctor__is_license_verified'),
                                       hospital_source_type=F('hospital__source_type'),
                                       hospital_is_live=F('hospital__is_live'),
                                       online_consultation_fees=F('doctor__online_consultation_fees')
                                       )
                             .filter(hospital_id__in=manageable_hosp_list)
                             # .values('hospital', 'doctor', 'hospital_name', 'doctor_name', 'doctor_gender',
                             #         'doctor_source_type', 'doctor_is_live', 'license',
                             #         'is_license_verified', 'hospital_source_type', 'hospital_is_live',
                             #         'online_consultation_fees')
                             .distinct('hospital', 'doctor')
                             )
        resp = []
        for obj in doc_hosp_queryset.all():
            resp_dict = {}
            resp_dict['hospital'] = obj.hospital.id
            resp_dict['doctor'] = obj.doctor.id
            resp_dict['hospital_name'] = obj.hospital_name
            resp_dict['doctor_name'] = obj.doctor_name
            resp_dict['doctor_gender'] = obj.doctor_gender
            resp_dict['doctor_source_type'] = obj.doctor_source_type
            resp_dict['doctor_is_live'] = obj.doctor_is_live
            resp_dict['license'] = obj.license
            resp_dict['is_license_verified'] = obj.is_license_verified
            resp_dict['hospital_source_type'] = obj.hospital_source_type
            resp_dict['hospital_is_live'] = obj.hospital_is_live
            resp_dict['online_consultation_fees'] = obj.online_consultation_fees
            partner_labs = list()
            hosp_lab_mappings = obj.hospital.partner_labs.all()
            for mapping in hosp_lab_mappings:
                lab_dict = {}
                lab = mapping.lab
                lab_dict['id'] = lab.id
                lab_dict['name'] = lab.name
                lab_dict['thumbnail'] = lab.get_thumbnail()
                lab_dict['is_b2b'] = lab.is_b2b
                partner_labs.append(lab_dict)
            resp_dict['partner_labs'] = partner_labs
            resp.append(resp_dict)
        return Response(resp)


class UserLabViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsDoctor,)

    @transaction.non_atomic_requests
    def list(self, request):
        user = request.user
        user_lab_queryset = Lab.objects.filter(
                                              Q(Q(manageable_lab_admins__user=user,
                                                  manageable_lab_admins__is_disabled=False,
                                                  manageable_lab_admins__write_permission=True) |
                                                Q(network__manageable_lab_network_admins__user=user,
                                                  network__manageable_lab_network_admins__is_disabled=False,
                                                  network__manageable_lab_network_admins__write_permission=True
                                                 )
                                                )
                                                 |
                                                (
                                                 Q(manageable_lab_admins__user=user,
                                                   manageable_lab_admins__is_disabled=False,
                                                   manageable_lab_admins__super_user_permission=True)
                                                 ),
                                               Q(is_live=True)
                                               ).values('id', 'name')
        return Response(user_lab_queryset)


class HospitalDoctorBillingPermissionViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsDoctor,)

    @transaction.non_atomic_requests
    def list(self, request):
        user = request.user

        queryset = GenericAdmin.objects.select_related('doctor', 'hospital')\
                                       .filter(Q
                                                  (Q(user=user,
                                                     is_disabled=False,
                                                     permission_type__in=[GenericAdmin.BILLINNG, GenericAdmin.ALL],
                                                     write_permission=True
                                                     ),
                                                   (
                                                     Q(Q(entity_type=GenericAdminEntity.DOCTOR,
                                                       doctor__doctor_clinics__hospital__is_billing_enabled=False),
                                                       (Q(hospital__isnull=False, doctor__doctor_clinics__hospital=F('hospital'))
                                                        |
                                                        Q(hospital__isnull=True)
                                                        )
                                                      )
                                                     |
                                                     Q(
                                                         Q(entity_type=GenericAdminEntity.HOSPITAL),
                                                         (Q(doctor__isnull=False,
                                                            hospital__hospital_doctors__doctor=F('doctor'))
                                                          |
                                                          Q(doctor__isnull=True)
                                                          )
                                                      )
                                                   )
                                                )
                                                |
                                                Q(
                                                    is_disabled=False,
                                                    super_user_permission=True,
                                                    user=user
                                                )
                                               )\
                                        .annotate(doctor_ids=F('hospital__hospital_doctors__doctor'),
                                                  doctor_names=F('hospital__hospital_doctors__doctor__name'),
                                                  hospital_name=F('hospital__name'),
                                                  doctor_name=F('doctor__name'),
                                                  hospital_ids=F('doctor__doctor_clinics__hospital'),
                                                  hospital_names=F('doctor__doctor_clinics__hospital__name')) \
                                        .values('doctor_ids', 'doctor_name', 'doctor_names', 'doctor_id',
                                                'hospital_ids', 'hospital_name', 'hospital_names', 'hospital_id')

        # doc_hosp_queryset = (
        #     DoctorClinic.objects.filter(
        #         Q(
        #           doctor__manageable_doctors__user=user,
        #           doctor__manageable_doctors__is_disabled=False,
        #           doctor__manageable_doctors__permission_type=GenericAdmin.BILLINNG,
        #           doctor__manageable_doctors__read_permission=True) |
        #         Q(
        #           hospital__manageable_hospitals__user=user,
        #           hospital__manageable_hospitals__is_disabled=False,
        #           hospital__manageable_hospitals__permission_type=GenericAdmin.BILLINNG,
        #           hospital__manageable_hospitals__read_permission=True))
        #         .values('hospital', 'doctor', 'hospital__manageable_hospitals__hospital', 'doctor__manageable_doctors__doctor')
        #         .annotate(doc_admin_doc=F('doctor__manageable_doctors__doctor'),
        #                   doc_admin_hosp=F('doctor__manageable_doctors__hospital'),
        #                   hosp_admin_doc=F('hospital__manageable_hospitals__doctor'),
        #                   hosp_admin_hosp=F('hospital__manageable_hospitals__hospital'),
        #                   hosp_name=F('hospital__name'), doc_name=F('doctor__name'))
        #     )

        resp_data = defaultdict(dict)
        for data in queryset:
            if data['hospital_ids']:
                temp_tuple = (data['doctor_id'], data['doctor_name'])
                if temp_tuple not in resp_data:
                    temp_dict = {
                        "admin_id": data["doctor_id"],
                        "level": Outstanding.DOCTOR_LEVEL,
                        "doctor_name": data["doctor_name"],
                        "hospital_list": list()
                    }
                    temp_dict["hospital_list"].append({
                        "id": data["hospital_ids"],
                        "name": data["hospital_names"]
                    })
                    resp_data[temp_tuple] = temp_dict
                else:
                    temp_name = {
                        "id": data["hospital_ids"],
                        "name": data["hospital_names"]
                    }
                    if temp_name not in resp_data[temp_tuple]["hospital_list"]:
                        resp_data[temp_tuple]["hospital_list"].append(temp_name)

            # if data['hosp_admin_doc'] is None and data['hosp_admin_hosp'] is not None:
            else:
                temp_tuple = (data['hospital_id'], data['hospital_name'])
                if temp_tuple not in resp_data:
                    temp_dict = {
                        "admin_id": data["hospital_id"],
                        "level": Outstanding.HOSPITAL_LEVEL,
                        "hospital_name": data["hospital_name"],
                        "doctor_list": list()
                    }
                    temp_dict["doctor_list"].append({
                        "id": data["doctor_ids"],
                        "name": data["doctor_names"]
                    })
                    resp_data[temp_tuple] = temp_dict
                else:
                    temp_name = {
                        "id": data["doctor_ids"],
                        "name": data["doctor_names"]
                    }
                    if temp_name not in resp_data[temp_tuple]["doctor_list"]:
                        resp_data[temp_tuple]["doctor_list"].append(temp_name)

        resp_data = [v for k,v in resp_data.items()]

        return Response(resp_data)

    def appointment_doc_hos_list(self, request):
        data = request.query_params
        admin_id = int(data.get("admin_id"))
        level = int(data.get("level"))
        user = request.user
        resp_data = list()
        if level == Outstanding.DOCTOR_LEVEL:
            permission = GenericAdmin.objects.filter(user=user, doctor=admin_id, permission_type=GenericAdmin.BILLINNG,
                                                     read_permission=True, is_disabled=False).exist()
            if permission:
                resp_data = DoctorClinic.objects.filter(doctor=admin_id).values('hospital', 'hospital__name')
        elif level == Outstanding.HOSPITAL_LEVEL:
            permission = GenericAdmin.objects.filter(user=user, hospital=admin_id, permission_type=GenericAdmin.BILLINNG,
                                                     read_permission=True, is_disabled=False).exist()
            if permission:
                resp_data = DoctorClinic.objects.filter(hospital=admin_id).values('doctor', 'doctor__name')
        elif level == Outstanding.HOSPITAL_NETWORK_LEVEL:
            permission = GenericAdmin.objects.filter(user=user, hospital_network=admin_id, permission_type=GenericAdmin.BILLINNG,
                                                     read_permission=True, is_disabled=False).exist()
            if permission:
                resp_data = DoctorClinic.objects.get(hospital__network=admin_id).values('hospital', 'doctor',
                                                                                          'hospital_name', 'doctor_name')
        elif level == Outstanding.LAB_LEVEL:
            pass
        elif level == Outstanding.LAB_NETWORK_LEVEL:
            pass

        return Response(resp_data)


class OrderViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated,)

    @transaction.non_atomic_requests
    def retrieve(self, request, pk):
        user = request.user
        params = request.query_params

        from_app = params.get("from_app", False)
        app_version = params.get("app_version", "1.0")

        order_obj = Order.objects.filter(pk=pk).first()

        if not (order_obj and order_obj.validate_user(user) and (
                order_obj.payment_status == Order.PAYMENT_PENDING or order_obj.is_cod_order)):
            return Response({"status": 0}, status.HTTP_404_NOT_FOUND)

        resp = dict()
        resp["status"] = 0

        if not order_obj:
            return Response(resp)

        # remove all cart_items => Workaround TODO: remove later
        if from_app and app_version and app_version <= "1.0":
            from keel.cart.models import Cart
            Cart.remove_all(user)

        resp["status"] = 1
        resp['data'], resp["payment_required"] = utils.payment_details(request, order_obj)
        resp['payment_options'], resp['invalid_payment_options'], resp['invalid_reason'] = PaymentOptions.filtered_payment_option(order_obj)
        return Response(resp)


class ConsumerAccountRefundViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsConsumer, )

    @transaction.atomic
    def refund(self, request):
        user = request.user
        consumer_account = ConsumerAccount.objects.get_or_create(user=user)
        consumer_account = ConsumerAccount.objects.select_for_update().get(user=user)
        if consumer_account.balance > 0:
            ctx_objs = consumer_account.debit_refund()
            if ctx_objs:
                for ctx_obj in ctx_objs:
                    ConsumerRefund.initiate_refund(user, ctx_obj)
        resp = dict()
        resp["status"] = 1
        return Response(resp)


class RefreshJSONWebToken(GenericViewSet):

    authentication_classes = (RefreshAuthentication,)

    def refresh(self, request):
        data = {}
        app_name = True if (request.META.get("HTTP_APP_NAME") and
                            (request.META.get("HTTP_APP_NAME") == 'docprime_consumer_app' or request.META.get("HTTP_APP_NAME") == 'd_web'))\
                        else None
        is_agent = False
        if hasattr(request, 'agent') and request.agent is not None:
            is_agent = True
        serializer = serializers.RefreshJSONWebTokenSerializer(data=request.data, context={'request': request, 'app_name': app_name, 'is_agent':is_agent})
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.validated_data

        # if 'active_session_error' in valid_data and valid_data['active_session_error']:
        #     return Response({'error': 'No Last Acctive Session Found'}, status=status.HTTP_401_UNAUTHORIZED)
        # if not serializer.is_valid():
        #     return Response({"error": "Cannot Refresh Token"}, status=status.HTTP_400_BAD_REQUEST)
        data['token'] = valid_data.get('token', '')
        data['user'] = valid_data.get('user', '')
        data['payload'] = valid_data.get('payload', '')
        data['is_agent'] = is_agent
        return Response(data)


class OnlineLeadViewSet(GenericViewSet):
    serializer_class = serializers.OnlineLeadSerializer

    def create(self, request):
        resp = {}
        data = request.data

        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            source = request.user_agent.os.family
        elif request.user_agent.is_pc:
            source = "WEB %s" % (data.get('source', ''))
        else:
            source = "Signup"

        data['source'] = source
        if not data.get('city_name'):
            data['city_name'] = 0
        serializer = serializers.OnlineLeadSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        if data.id:
            resp['status'] = 'success'
            resp['id'] = data.id
        return Response(resp)


class CareerViewSet(GenericViewSet):
    serializer_class = serializers.CareerSerializer

    def upload(self, request):
        resp = {}
        serializer = serializers.CareerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        if data.id:
            resp['status'] = 'success'
            resp['id'] = data.id
        return Response(resp)


class SendBookingUrlViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def send_booking_url(self, request):
        type = request.data.get('type')
        purchase_type = request.data.get('purchase_type', None)
        utm_tags = request.data.get('utm_spo_tags', {})
        if not utm_tags:
            utm_tags = {}
        utm_source = utm_tags.get('utm_source', {})
        landing_url = request.data.get('landing_url', '')
        message_medium = request.data.get('message_medium', None)

        # agent_token = AgentToken.objects.create_token(user=request.user)
        user_token = JWTAuthentication.generate_token(request.user, request)
        token = user_token['token'].decode("utf-8") if 'token' in user_token else None
        user_profile = None

        if request.user.is_authenticated:
            user_profile = request.user.get_default_profile()

        if purchase_type == PlusDummyData.DataType.SINGLE_PURCHASE:
            if not landing_url:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No Landing url found.'})
            SmsNotification.send_single_purchase_booking_url(token, str(request.user.phone_number), utm_source=utm_source, landing_url=landing_url, user_id=request.user.id)
            if message_medium == 'WHATSAPP':
                self.send_whatsapp(request, token, utm_source, landing_url)
            return Response({"status": 1})

        if purchase_type == 'vip_purchase':
            SmsNotification.send_vip_booking_url(token, str(request.user.phone_number), utm_source=utm_source, user_id=request.user.id)
            if message_medium == 'WHATSAPP':
                self.send_whatsapp(request, token, utm_source, "vip-club-member-details")
            return Response({"status": 1})

        if not user_profile:
            return Response({"status": 1})
        if purchase_type == 'insurance':
            SmsNotification.send_insurance_booking_url(token=token, phone_number=str(user_profile.phone_number), user=user_profile.user)
            EmailNotification.send_insurance_booking_url(token=token, email=user_profile.email, user=user_profile.user)
        elif purchase_type == 'endorsement':
            SmsNotification.send_endorsement_request_url(token=token, phone_number=str(user_profile.phone_number), user=user_profile.user)
            EmailNotification.send_endorsement_request_url(token=token, email=user_profile.email, user=user_profile.user)
        else:
            booking_url = SmsNotification.send_booking_url(token=token, phone_number=str(user_profile.phone_number), name=user_profile.name,  user=user_profile.user)
            EmailNotification.send_booking_url(token=token, email=user_profile.email, user=user_profile.user)

        if message_medium == 'WHATSAPP':
            self.send_whatsapp(request, token, utm_source, landing_url)

        return Response({"status": 1})

    def send_whatsapp(self, request, token, utm_source, landing_url):
        whatsapp_template = 'gold_payment_template'
        utm_source = utm_source.get('utm_source', {})
        booking_url = "{}/agent/booking?user_id={}&token={}".format(settings.CONSUMER_APP_DOMAIN, request.user.id,
                                                                    token)
        if utm_source:
            booking_url = booking_url + "&callbackurl={landing_url}&utm_source={utm_source}&is_agent=false".format(
                landing_url=landing_url, utm_source=utm_source)
        else:
            booking_url = booking_url + "&callbackurl={landing_url}&is_agent=false".format(
                landing_url=landing_url)
        short_url = generate_short_url(booking_url)
        whatsapp_payload = [short_url]
        WhtsappNotification.send_whatsapp(request.user.phone_number, whatsapp_template, whatsapp_payload, None)


class SendCartUrlViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def send_cart_url(self, request):
        # order_id = request.data.get('orderId', None)
        utm_source = request.data.get('utm_source')
        utm_term = request.data.get('utm_term')
        utm_medium = request.data.get('utm_medium')
        utm_campaign = request.data.get('utm_campaign')

        utm_parameters = ""
        if utm_source:
            utm_source = "utm_source=%s&" % utm_source
            utm_parameters = utm_parameters + utm_source
        if utm_term:
            utm_term = "utm_term=%s&" % utm_term
            utm_parameters = utm_parameters + utm_term
        if utm_medium:
            utm_medium = "utm_medium=%s&" % utm_medium
            utm_parameters = utm_parameters + utm_medium
        if utm_campaign:
            utm_campaign = "utm_campaign=%s" % utm_campaign
            utm_parameters = utm_parameters + utm_campaign

        user_token = JWTAuthentication.generate_token(request.user, request)
        token = user_token['token'].decode("utf-8") if 'token' in user_token else None
        user_profile = None

        if request.user.is_authenticated:
            user_profile = request.user.get_default_profile()
        if not user_profile:
            return Response({"status": 1})

        SmsNotification.send_cart_url(token=token, phone_number=str(user_profile.phone_number), utm=utm_parameters, user= user_profile.user)

        return Response({"status": 1})


class OrderDetailViewSet(GenericViewSet):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.OrderDetailDoctorSerializer

    @transaction.non_atomic_requests
    def details(self, request, order_id):
        if not order_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = Order.objects.filter(id=order_id).first()
        if not queryset.validate_user(request.user):
            return Response({"status": 0}, status.HTTP_404_NOT_FOUND)

        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)
        resp = dict()

        if queryset.product_id == Order.DOCTOR_PRODUCT_ID:
            serializer = serializers.OrderDetailDoctorSerializer(queryset)
            resp = serializer.data
            procedure_ids = []
            if queryset.action_data:
                action_data = queryset.action_data
                if action_data.get('extra_details'):
                    extra_details = action_data.get('extra_details')
                    for data in extra_details:
                        if data.get('procedure_id'):
                            procedure_ids.append(int(data.get('procedure_id')))
            resp['procedure_ids'] = procedure_ids

        elif queryset.product_id == Order.LAB_PRODUCT_ID:
            serializer = serializers.OrderDetailLabSerializer(queryset)
            resp = serializer.data

        return Response(resp)

    @transaction.non_atomic_requests
    def summary(self, request, order_id):
        from keel.api.v1.cart import serializers as cart_serializers
        from keel.api.v1.utils import convert_datetime_str_to_iso_str

        if not order_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order_data = Order.objects.filter(id=order_id).first()

        if not order_data:
            return Response({"message": "Invalid order ID"}, status.HTTP_404_NOT_FOUND)

        if not order_data.validate_user(request.user):
            return Response({"status": 0}, status.HTTP_404_NOT_FOUND)

        if not order_data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        processed_order_data = []
        valid_for_cod_to_prepaid = order_data.is_cod_order
        if order_data.is_parent():
            child_orders = order_data.orders.all()
        else:
            child_orders = [order_data]

        class OrderCartItemMapper():
            def __init__(self, order_obj):
                self.data = order_obj.action_data
                self.order = order_obj

        for order in child_orders:
            cod_deal_price = None
            enabled_for_cod = False
            # opd_appoint = OpdAppointment.objects.filter(id=order.reference_id)[0]
            opd_appoint = OpdAppointment.objects.filter(id=order.reference_id).first()
            if opd_appoint:
                start_time = opd_appoint.time_slot_start
                day = start_time.weekday()

            if opd_appoint and opd_appoint.payment_type == OpdAppointment.COD:
                # doc_clinic_timing = DoctorClinicTiming.objects.filter(day=day, doctor_clinic__doctor=opd_appoint.doctor, doctor_clinic__hospital=opd_appoint.hospital)[0]
                doc_clinic_timing = DoctorClinicTiming.objects.filter(day=day, doctor_clinic__doctor=opd_appoint.doctor,
                                                                      doctor_clinic__hospital=opd_appoint.hospital).first()
                if doc_clinic_timing:
                    cod_deal_price = doc_clinic_timing.dct_cod_deal_price()
                    enabled_for_cod = doc_clinic_timing.is_enabled_for_cod()

            item = OrderCartItemMapper(order)
            temp_time_slot_start = None
            temp_test_time_slots = []
            # if order.action_data.get('multi_timings_enabled'):
            #     for test_time_slot in order.action_data.get('test_time_slots'):
            #         test_id = test_time_slot.get('test_id')
            #         test_data = dict()
            #         test_data['test_id'] = test_id
            #         test_data['time_slot_start'] = convert_datetime_str_to_iso_str(test_time_slot.get('time_slot_start'))
            #         test_data['is_home_pickup'] = test_time_slot.get('is_home_pickup')
            #         temp_test_time_slots.append(test_data)
            # else:
            #     temp_time_slot_start = convert_datetime_str_to_iso_str(order.action_data["time_slot_start"])
            temp_time_slot_start = convert_datetime_str_to_iso_str(order.action_data["time_slot_start"])

            appointment = None
            appointment_amount = 0
            if order.product_id == Order.DOCTOR_PRODUCT_ID:
                appointment = opd_appoint
                appointment_amount = appointment.mrp if appointment else 0
            elif order.product_id == Order.LAB_PRODUCT_ID:
                appointment = LabAppointment.objects.filter(id=order.reference_id).first()
                appointment_amount = appointment.price if appointment else 0

            plus_appointment_mapping = None
            if appointment:
                plus_appointment_mapping = PlusAppointmentMapping.objects.filter(object_id=appointment.id).first()

            payment_mode = ''
            if appointment:
                payment_modes = dict(OpdAppointment.PAY_CHOICES)
                if payment_modes:
                    effective_price = appointment.effective_price
                    payment_type = appointment.payment_type
                    if effective_price > 0 and payment_type == 5:
                        payment_mode = 'Online'
                    else:
                        payment_mode = payment_modes.get(appointment.payment_type, '')

            appointment_via_sbi = list()
            if order.action_data.get('utm_sbi_tags', None):
                appointment_via_sbi.append(True)

            curr = {
                "mrp": order.action_data["mrp"] if "mrp" in order.action_data else order.action_data["agreed_price"],
                "deal_price": order.action_data["deal_price"],
                "effective_price": order.action_data["effective_price"],
                "discount": order.action_data.get('discount', 0),
                "data": cart_serializers.CartItemSerializer(item, context={"validated_data": None}).data,
                "booking_id": order.reference_id,
                "time_slot_start": temp_time_slot_start,
                "test_time_slots": temp_test_time_slots,
                "payment_type": order.action_data["payment_type"],
                "cod_deal_price": cod_deal_price,
                "enabled_for_cod": enabled_for_cod,
                "is_gold_member": True if appointment and appointment.plus_plan and appointment.plus_plan.plan.is_gold else False,
                "is_vip_member": True if appointment and appointment.plus_plan and not appointment.plus_plan.plan.is_gold else False,
                "covered_under_vip": True if appointment and appointment.plus_plan else False,
                'vip_amount': appointment_amount - plus_appointment_mapping.amount if plus_appointment_mapping else 0,
                "payment_mode": payment_mode
            }
            processed_order_data.append(curr)

        appointment_sbi = False
        if True in appointment_via_sbi:
            appointment_sbi = True

        return Response({"data": processed_order_data, "valid_for_cod_to_prepaid": valid_for_cod_to_prepaid,
                         "appointment_via_sbi": appointment_sbi})


class UserTokenViewSet(GenericViewSet):

    @transaction.non_atomic_requests
    def details(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        agent_token = AgentToken.objects.filter(token=token, is_consumed=False, expiry_time__gte=timezone.now()).first()
        if agent_token:
            token_object = JWTAuthentication.generate_token(agent_token.user, request)
            # agent_token.is_consumed = True
            agent_token.save()
            return Response({"status": 1, "token": token_object['token'], 'order_id': agent_token.order_id})
        else:
            return Response({"status": 0}, status=status.HTTP_400_BAD_REQUEST)


class ContactUsViewSet(GenericViewSet):

    def create(self, request):
        serializer = serializers.ContactUsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        ContactUs.objects.create(**validated_data)
        return Response({'message': 'success'})


class DoctorNumberAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Doctor.objects.all()
        # dn = DoctorNumber.objects.values_list('doctor', flat=True)
        #
        # qs = Doctor.objects.exclude(id__in=dn)
        if self.q:
            qs = qs.filter(name__icontains=self.q).order_by('name')
        return qs

class UserLeadViewSet(GenericViewSet):

    def create(self,request):
        resp = {}
        serializer = serializers.UserLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data:
            resp['name'] = validated_data.get('name')
            resp['message'] = validated_data.get('message')
            resp['phone_number'] = validated_data.get('phone_number')
            resp['gender'] = validated_data.get('gender')

            ul_obj = UserLead.objects.create(**resp)
            resp['status'] = "success"


        return Response(resp)


class UserRatingViewSet(GenericViewSet):

    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsConsumer )

    def get_queryset(self):
        return None

    def list_ratings(self,request):
        resp = []
        user = request.user
        queryset = rate_models.RatingsReview.objects.select_related('content_type')\
                                                    .prefetch_related('content_object', 'compliment')\
                                                    .filter(user=user).order_by('-updated_at')
        if len(queryset):
            for obj in queryset:
                compliments_string = ''
                address = ''
                c_list = []
                cid_list = []
                if obj.content_type == ContentType.objects.get_for_model(Doctor):
                    name = obj.content_object.get_display_name()
                    if obj.appointment_id:
                        appointment = OpdAppointment.objects.select_related('hospital').filter(id=obj.appointment_id).first()
                        if appointment:
                            address = appointment.hospital.get_hos_address()
                elif obj.content_type == ContentType.objects.get_for_model(Lab):
                    name = obj.content_object.name
                    address = obj.content_object.get_lab_address()
                else:
                    name = obj.content_object.name
                    address = obj.content_object.get_hos_address()
                for cm in obj.compliment.all():
                    c_list.append(cm.message)
                    cid_list.append(cm.id)
                if c_list:
                    compliments_string = (', ').join(c_list)
                rating_obj = {}
                rating_obj['id'] = obj.id
                rating_obj['ratings'] = obj.ratings
                rating_obj['address'] = address
                rating_obj['review'] = obj.review
                rating_obj['entity_name'] = name
                rating_obj['entity_id'] = obj.object_id
                rating_obj['date'] = obj.updated_at.strftime('%b %d, %Y')
                rating_obj['compliments'] = compliments_string
                rating_obj['compliments_list'] = cid_list
                rating_obj['appointment_id'] = obj.appointment_id
                rating_obj['appointment_type'] = obj.appointment_type
                rating_obj['icon'] = request.build_absolute_uri(obj.content_object.get_thumbnail())
                resp.append(rating_obj)
        return Response(resp)


class AppointmentViewSet(viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def upcoming_appointments(self, request):
        all_appointments = []
        try:
            user_id = request.user.id
            all_appointments = get_all_upcoming_appointments(user_id)
        except Exception as e:
            logger.error(str(e))
        return Response(all_appointments)

    def get_queryset(self):
        return OpdAppointment.objects.none()


class DoctorScanViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsNotAgent)

    # @transaction.atomic
    def doctor_qr_scan(self, request, pk):
        opdapp_obj = OpdAppointment.objects.filter(pk=pk).first()
        request_url = request.data.get('url')
        type = request.data.get('type')
        user = request.user

        if not opdapp_obj:
            return Response('Opd Appointment does not exist', status.HTTP_400_BAD_REQUEST)

        if not user == opdapp_obj.user:    
            return Response('Unauthorized User', status.HTTP_401_UNAUTHORIZED)

        if not request_url:
            return Response('URL not given', status.HTTP_400_BAD_REQUEST)

        if not type == 'doctor':
            return Response('Invalid type', status.HTTP_400_BAD_REQUEST)

        if not len(opdapp_obj.doctor.qr_code.all()):
            return Response('QRCode not enabled for this doctor', status.HTTP_400_BAD_REQUEST)


        appt_status = opdapp_obj.status
        url = opdapp_obj.doctor.qr_code.first().data
        complete_with_qr_scanner = True

        if not url:
            return Response('URL not found', status.HTTP_400_BAD_REQUEST)

        url = url.get('url', None)
        if not request_url == url:
            return Response('Invalid url', status.HTTP_400_BAD_REQUEST)

        if not appt_status == OpdAppointment.ACCEPTED or not complete_with_qr_scanner == True:
            return Response('Bad request', status.HTTP_400_BAD_REQUEST)


        opdapp_obj.action_completed()
        resp = AppointmentRetrieveSerializer(opdapp_obj, context={"request": request})
        return Response(resp.data)


class TokenFromUrlKey(viewsets.GenericViewSet):

    def get_token(self, request):
        from keel.authentication.models import ClickLoginToken
        serializer = serializers.TokenFromUrlKeySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = data.get("auth_token")
        key = data.get("key")
        if token:
            return Response({'status': 1, 'token': token})
        elif key:
            obj = ClickLoginToken.objects.filter(url_key=key).first()
            if obj:
                obj.is_consumed = True
                obj.save()
                LastLoginTimestamp.objects.create(user=obj.user, source="d_sms")
                return Response({'status': 1, 'token': obj.token})
            else:
                return Response({'status': 0, 'token': None, 'message': 'key not found'}, status=status.HTTP_404_NOT_FOUND)


class ProfileEmailUpdateViewset(viewsets.GenericViewSet):
    authentication_classes = (JWTAuthentication, )
    # permission_classes = (IsAuthenticated, IsNotAgent)
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        request_data = request.data

        serializer = serializers.ProfileEmailUpdateInitSerializer(data=request_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        obj = UserProfileEmailUpdate.objects.filter(profile=data['profile'], old_email=data['profile'].email,
                                                    new_email=data['email']).filter(~Q(otp=None)).order_by('id').last()
        if obj and obj.is_request_alive():
            obj.send_otp_email()
            return Response({'success': True, 'id': obj.id})

        obj_id = None

        try:
            obj = UserProfileEmailUpdate.initiate(data['profile'], data['email'])
            obj_id = obj.id
        except Exception as e:
            logger.error(str(e))
            return Response({'success': False})

        return Response({'success': True, 'id': obj_id})

    def update_email(self, request):
        request_data = request.data

        serializer = serializers.ProfileEmailUpdateProcessSerializer(data=request_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        obj = UserProfileEmailUpdate.objects.filter(profile=data['profile'], id=data['id'], is_successfull=False).first()
        if not obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if obj.otp_verified:
            return Response({'success': True, 'message': 'OTP verified successfully.'})

        if not obj.is_request_alive():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'success': False, 'message': 'Given otp has been expired.'})

        if obj.otp != data['otp']:
            return Response(data={'success': False, 'message': 'Please enter a valid OTP.'})

        is_changed = obj.process_email_change(obj.otp, data.get('process_immediately', False))
        if not is_changed:
            return Response({'success': False})

        return Response({'success': True, 'message': 'OTP verified successfully.'})


class MatrixUserViewset(GenericViewSet):
    authentication_classes = (MatrixUserAuthentication,)

    @transaction.atomic()
    def user_login_via_matrix(self, request):
        from django.http import JsonResponse
        response = {'login': 0}
        if request.method != 'POST':
            return JsonResponse(response, status=405)
        serializer = serializers.MatrixUserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        doctor = data.get('doctor')
        hospital = data.get('hospital')
        if not doctor:
            return Response({"error": "Invalid Doctor ID"}, status=status.HTTP_400_BAD_REQUEST)
        if not hospital:
            return Response({'error': "Invalid Hospital ID"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_data = User.get_external_login_data(data, request)
        except Exception as e:
            logger.error(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        token = user_data.get('token')
        if not token:
            return JsonResponse(response, status=400)

        base_landing_url = settings.BASE_URL + '/sms/booking?token={}&user_id={}'.format(token['token'].decode("utf-8"), user_data.get('user_id'))
        # redirect_url = 'search' if redirect_type == 'lab' else '/'
        redirect_url = 'opd/doctor/{}/{}/bookdetails?is_matrix=true'.format(doctor.id, hospital.id)
        callback_url = base_landing_url + "&callbackurl={}".format(redirect_url)
        docprime_login_url = generate_short_url(callback_url)

        response = {
            "docprime_url": docprime_login_url
        }

        return Response(response, status=status.HTTP_200_OK)


class ExternalLoginViewSet(GenericViewSet):
    SBIG = 1
    BAGIC = 2

    @transaction.atomic()
    def get_external_login_response(self, request, ext_type=0):
        from django.http import JsonResponse
        response = {'login': 0}
        if request.method != 'POST':
            return JsonResponse(response, status=405)

        serializer = serializers.ExternalLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        redirect_type = data.get('redirect_type')
        user_data = User.get_external_login_data(data, request)
        token_object = user_data.get('token', None)
        if not token_object or not user_data:
            return Response({'error': 'Unauthorise'}, status=status.HTTP_400_BAD_REQUEST)

        base_url = settings.BASE_URL
        if ext_type == 1:
            base_url = settings.SBIG_BASE_URL

        base_landing_url = base_url + '/sms/booking?token={}&user_id={}'.format(token_object['token'].decode("utf-8"), user_data.get('user_id'))
        redirect_url = 'lab' if redirect_type == 'lab' else 'opd'
        callback_url = base_landing_url + "&callbackurl={}".format(redirect_url)
        docprime_login_url = generate_short_url(callback_url)

        response = {
            "docprime_url": docprime_login_url
        }

        return Response(response, status=status.HTTP_200_OK)


class BajajAllianzUserViewset(GenericViewSet):
    authentication_classes = (BajajAllianzAuthentication,)

    @transaction.atomic()
    def user_login_via_bagic(self, request):
        ext_type = ExternalLoginViewSet.BAGIC
        response = ExternalLoginViewSet().get_external_login_response(request, ext_type)
        return response


class SbiGUserViewset(GenericViewSet):
    authentication_classes = (SbiGAuthentication,)

    @transaction.atomic()
    def user_login_via_sbig(self, request):
        ext_type = ExternalLoginViewSet.SBIG
        response = ExternalLoginViewSet().get_external_login_response(request, ext_type)
        return response


class PGRefundViewSet(viewsets.GenericViewSet):

    permission_classes = (utils.IsPGRequest, )
    @transaction.atomic()
    def save_pg_refund(self, request):
        response = {'status': 0}
        if request.method != 'POST':
            return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = serializers.PGRefundSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        refund_obj = data['refund_obj']
        try:
            refund_obj.pg_transaction.amount = data.get('txnAmount')
            refund_obj.pg_transaction.pb_gateway_name = data.get('gateway')
            refund_obj.pg_transaction.payment_mode = data.get('mode')
            refund_obj.refund_amount = data.get('refundAmount')

            refund_obj.bank_arn = data.get('bank_arn')
            refund_obj.bankRefNum = data.get('bankRefNum')
            refund_obj.refundDate = utils.aware_time_zone(data.get('refundDate'))
            refund_obj.refundId = data.get('refundId')
            refund_obj.pg_transaction.save()
            refund_obj.save()
        except Exception as e:
            logger.error(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status':1}, status=status.HTTP_200_OK)

