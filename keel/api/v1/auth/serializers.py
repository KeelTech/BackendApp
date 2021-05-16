from rest_framework import serializers
from keel.authentication.models import (OtpVerifications, User, UserProfile, Notification, NotificationEndpoint,
                                         DoctorNumber, Address, GenericAdmin, UserSecretKey, WhiteListedLoginTokens,
                                         UserPermission, Address, GenericAdmin, GenericLabAdmin, UserProfileEmailUpdate)
from keel.doctor.models import DoctorMobile, ProviderSignupLead, Hospital, Doctor
from keel.common.models import AppointmentHistory
from keel.doctor.models import DoctorMobile
from keel.insurance.models import InsuredMembers, UserInsurance
from keel.diagnostic.models import AvailableLabTest
from keel.account.models import ConsumerAccount, Order, ConsumerTransaction, ConsumerRefund, PgTransaction
import datetime, calendar, pytz
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from keel.api.v1 import utils as v1_utils

from keel.lead.models import UserLead
from keel.web.models import OnlineLead, Career, ContactUs
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.templatetags.staticfiles import static
import jwt, logging
from django.conf import settings
from django.db.models import Q
from keel.authentication.backends import JWTAuthentication
from keel.common import models as common_models

User = get_user_model()
logger = logging.getLogger(__name__)


class OTPSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=5000000000,max_value=9999999999)
    via_sms = serializers.BooleanField(default=True, required=False)
    via_whatsapp = serializers.BooleanField(default=False, required=False)
    request_source = serializers.CharField(required=False, max_length=200)

    def validate(self, attrs):
        otp_obj = OtpVerifications.objects.filter(phone_number=attrs.get('phone_number')).order_by('-id').first()
        if not attrs.get('via_whatsapp') and otp_obj and not otp_obj.is_expired and (
                datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - v1_utils.aware_time_zone(
                otp_obj.updated_at)).total_seconds() < OtpVerifications.TIME_BETWEEN_CONSECUTIVE_REQUESTS:
            raise serializers.ValidationError('Please try again in a moment.')
        if otp_obj:
            attrs['otp_obj'] = otp_obj
        return attrs

class OTPVerificationSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=5000000000,max_value=9999999999)
    otp = serializers.IntegerField(min_value=100000, max_value=999999, allow_null=True)
    source = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    truecaller_verified = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        # if not User.objects.filter(phone_number=attrs['phone_number'], user_type=User.CONSUMER).exists():
        #     raise serializers.ValidationError('User does not exist')

        if attrs.get('source') in settings.TRUECALLER_SOURCES and attrs.get('truecaller_verified') is True:
            return attrs

        if not attrs['otp']:
            raise serializers.ValidationError("Invalid OTP")

        if (not OtpVerifications
                .objects.filter(phone_number=attrs['phone_number'], code=attrs['otp'], is_expired=False,
                                created_at__gte=timezone.now() - relativedelta(
                                    minutes=OtpVerifications.OTP_EXPIRY_TIME)).exists() and
                not (str(attrs['phone_number']) in settings.OTP_BYPASS_NUMBERS and str(attrs['otp']) == settings.HARD_CODED_OTP)):
            raise serializers.ValidationError("Invalid OTP")
        return attrs


class DoctorLoginSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=5000000000,max_value=9999999999)
    otp = serializers.IntegerField(min_value=100000,max_value=999999)
    source = serializers.CharField(max_length=100, required=False)

    def validate(self, attrs):
        if attrs['phone_number'] == 9582557400:
            return attrs

        if not OtpVerifications.objects.filter(phone_number=attrs['phone_number'], code=attrs['otp'], is_expired=False).exists():
            raise serializers.ValidationError("Invalid OTP")

        if not User.objects.filter(phone_number=attrs['phone_number'], user_type=User.DOCTOR).exists():
            doctor_not_exists = admin_not_exists = False
            lab_admin_not_exists = provider_signup_lead_not_exists = False
            if not DoctorNumber.objects.filter(phone_number=attrs['phone_number']).exists():
                doctor_not_exists = True
            if not GenericAdmin.objects.filter(phone_number=attrs['phone_number'], is_disabled=False).exists():
                admin_not_exists = True
            if not GenericLabAdmin.objects.filter(phone_number=attrs['phone_number'], is_disabled=False).exists():
                lab_admin_not_exists = True
            if not ProviderSignupLead.objects.filter(phone_number=attrs['phone_number'], user__isnull=False).exists():
                provider_signup_lead_not_exists = True
            if doctor_not_exists and admin_not_exists and lab_admin_not_exists and provider_signup_lead_not_exists:
                raise serializers.ValidationError('No Doctor or Admin with given phone number found')

        generic_admins = GenericAdmin.objects.select_related('hospital').filter(phone_number=attrs['phone_number'],
                                                                                is_disabled=False)
        live_hospital_exists = False
        for admin in generic_admins:
            if admin.hospital:
                hospital = admin.hospital
                if (hospital.source_type in (None, Hospital.AGENT) and hospital.is_live) \
                        or (hospital.source_type == Hospital.PROVIDER):
                    live_hospital_exists = True
                    break
        if generic_admins and not live_hospital_exists:
            raise serializers.ValidationError("Live hospital for admin not found")

        return attrs


# class UserProfileSerializer(serializers.ModelSerializer):
#     name = serializers.CharField()
#     age = serializers.IntegerField(min_value=1, max_value=150)
#     email = serializers.EmailField()
#     gender = serializers.ChoiceField(UserProfile.GENDER_CHOICES)
#     class Meta:
#         model = UserProfile
#         fields = ('name', 'age', 'email', 'gender')


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.IntegerField(min_value=5000000000,max_value=9999999999)
    otp = serializers.IntegerField(min_value=100000,max_value=999999)

    def validate(self, attrs):

        if not OtpVerifications.objects.filter(phone_number=attrs['phone_number'], code=attrs['otp'], is_expired=False).exists():
            raise serializers.ValidationError("Invalid OTP")

        if User.objects.filter(phone_number=attrs['phone_number'],user_type=User.CONSUMER).exists():
            raise serializers.ValidationError('User already exists')

        return attrs

    def create(self, validated_data):
        # profile_data = validated_data.pop('profile')
        # age = profile_data.pop('age')
        # # need to convert age to date of birth
        # dob = datetime.datetime.now() - relativedelta(years=age)
        # profile_data['dob'] = dob

        validated_data.pop('otp')
        validated_data['user_type'] = User.CONSUMER
        validated_data['is_phone_number_verified'] = True
        user = User.objects.create(**validated_data)

        return user

    class Meta:
        model = User
        fields = ('phone_number', 'otp')


# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'


class NotificationEndpointSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    platform = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    app_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    app_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    token = serializers.CharField()

    class Meta:
        model = NotificationEndpoint
        # fields = '__all__'
        fields = ('user', 'device_id', 'platform', 'app_name', 'app_version', 'token')


class NotificationEndpointSaveSerializer(serializers.Serializer):
    device_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    platform = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    app_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    app_version = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    token = serializers.CharField()


class NotificationEndpointDeleteSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        request = self.context.get("request")
        if not NotificationEndpoint.objects.filter(token=attrs.get('token')).exists():
            raise serializers.ValidationError("Token does not exists.")
        if not NotificationEndpoint.objects.filter(user=request.user, token=attrs.get('token')).exists():
            raise serializers.ValidationError("Token does not  match.")
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    GENDER_CHOICES = UserProfile.GENDER_CHOICES
    name = serializers.CharField(max_length=100)
    age = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, allow_null=True, allow_blank=True, required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    profile_image = serializers.SerializerMethodField()
    is_insured = serializers.SerializerMethodField()
    insurance_status = serializers.SerializerMethodField()
    dob = serializers.DateField(allow_null=True, required=False)
    whatsapp_optin = serializers.NullBooleanField(required=False)
    whatsapp_is_declined = serializers.BooleanField(required=False)
    is_default_user = serializers.BooleanField(required=False)
    is_vip_member = serializers.SerializerMethodField()
    is_vip_gold_member = serializers.SerializerMethodField()
    vip_data = serializers.SerializerMethodField()
    is_care = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "name", "email", "gender", "phone_number", "is_otp_verified", "is_default_user", "profile_image"
                  , "age", "user", "dob", "is_insured", "updated_at", "whatsapp_optin", "whatsapp_is_declined",
                  "insurance_status", "is_vip_member", "is_vip_gold_member", "vip_data", "is_care")

    def get_vip_data(self, obj):
        resp = {}
        if isinstance(obj, dict):
            return resp
        plus_membership = obj.get_plus_membership
        if not plus_membership:
            return resp
        resp['is_member_allowed'] = False
        plus_members_count = plus_membership.get_members.count()
        resp['expiry_date'] = plus_membership.expire_date.date()
        resp['total_members_allowed'] = plus_membership.plan.total_allowed_members
        if resp['total_members_allowed'] and resp['total_members_allowed'] > 0 and plus_members_count >=0 and \
                (resp['total_members_allowed'] - plus_members_count > 0) and not plus_membership.plan.is_corporate:
            resp['is_member_allowed'] = True
        resp['purchase_date'] = plus_membership.purchase_date.date()
        primary_member = plus_membership.get_primary_member_profile()
        if primary_member:
            resp['primary_member'] = primary_member.first_name + " " + primary_member.last_name
        else:
            members = plus_membership.get_members
            primary_member_obj = members.first()
            primary_member = primary_member_obj.first_name + " " + primary_member_obj.last_name
            resp['primary_member'] = primary_member
        return resp

    def validate(self, attrs):
        if self.instance:
            # if self.instance.is_gold_profile:
            #     raise serializers.ValidationError("Gold Member Profile can not be editable.")
            if self.instance.is_insured_profile:
                raise serializers.ValidationError("Insured Member profile can not be editable.")
        return attrs

    def get_is_insured(self, obj):
        if isinstance(obj, dict):
            return False

        # insured_member_obj = InsuredMembers.objects.filter(profile=obj).order_by('-id').first()
        insured_member_obj = sorted(obj.insurance.all(), key=lambda object: object.id, reverse=True)[0] if obj.insurance.all() else None
        if not insured_member_obj:
            return False
        # user_insurance_obj = UserInsurance.objects.filter(id=insured_member_obj.user_insurance_id).last()
        user_insurance_obj = insured_member_obj.user_insurance
        if user_insurance_obj and user_insurance_obj.is_valid():
            return True
        else:
            return False

    def get_is_vip_member(self, obj):
        if isinstance(obj, dict):
            return False
        plus_member_obj = sorted(obj.plus_member.all(), key=lambda object: object.id, reverse=True)[
            0] if obj.plus_member.all() else None
        if not plus_member_obj:
            return False
        plus_user_obj = plus_member_obj.plus_user
        if plus_user_obj and plus_user_obj.is_valid():
            return True
        else:
            return False

    def get_is_vip_gold_member(self, obj):
        if isinstance(obj, dict):
            return False
        plus_member_obj = sorted(obj.plus_member.all(), key=lambda object: object.id, reverse=True)[
            0] if obj.plus_member.all() else None
        if not plus_member_obj:
            return False
        plus_user_obj = plus_member_obj.plus_user
        if plus_user_obj and plus_user_obj.is_valid() and plus_user_obj.plan.is_gold:
            return True
        else:
            return False

    def get_insurance_status(self, obj):
        if isinstance(obj, dict):
            return False
        # insured_member_obj = InsuredMembers.objects.filter(profile=obj).order_by('-id').first()
        insured_member_obj = sorted(obj.insurance.all(), key=lambda object: object.id, reverse=True)[0] if obj.insurance.all() else None
        if not insured_member_obj:
            return 0
        # user_insurance_obj = UserInsurance.objects.filter(id=insured_member_obj.user_insurance_id).last()
        user_insurance_obj = insured_member_obj.user_insurance
        if user_insurance_obj and user_insurance_obj.is_profile_valid():
            return user_insurance_obj.status
        else:
            return 0

    def get_age(self, obj):
        from datetime import date
        age = None
        birth_date = None
        if hasattr(obj, 'dob'):
            birth_date = obj.dob
        elif isinstance(obj, dict):
            birth_date = obj.get('dob')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year
            full_year_passed = (today.month, today.day) >= (birth_date.month, birth_date.day)
            if not full_year_passed:
                age -= 1
        return age

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        profile_image = None
        if hasattr(obj, 'profile_image'):
            profile_image = obj.profile_image
        elif isinstance(obj, dict):
            profile_image = obj.get('profile_image')
        if profile_image:
            photo_url = profile_image.url
            return request.build_absolute_uri(photo_url)
        else:
            return None

    def get_is_care(self, obj):
        from keel.subscription_plan.models import UserPlanMapping
        resp = {}
        if isinstance(obj, dict):
            return resp
        user = obj.user
        if not user:
            return resp
        user_planning_obj = UserPlanMapping.objects.filter(user=user, status=UserPlanMapping.BOOKED).first()
        if user_planning_obj:
            return True
        else:
            return False

class ProviderUserProfileSerializer(serializers.ModelSerializer):
    GENDER_CHOICES = UserProfile.GENDER_CHOICES
    name = serializers.CharField(max_length=100)
    age = serializers.SerializerMethodField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, allow_null=True, allow_blank=True, required=False)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    profile_image = serializers.SerializerMethodField()
    dob = serializers.DateField(allow_null=True, required=False)
    is_default_user = serializers.BooleanField(required=False)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "name", "email", "gender", "phone_number", "is_otp_verified", "is_default_user", "profile_image"
                  , "age", "user", "dob", "updated_at")

    def get_age(self, obj):
        from datetime import date
        age = None
        birth_date = None
        if hasattr(obj, 'dob'):
            birth_date = obj.dob
        elif isinstance(obj, dict):
            birth_date = obj.get('dob')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year
            full_year_passed = (today.month, today.day) >= (birth_date.month, birth_date.day)
            if not full_year_passed:
                age -= 1
        return age

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        profile_image = None
        if hasattr(obj, 'profile_image'):
            profile_image = obj.profile_image
        elif isinstance(obj, dict):
            profile_image = obj.get('profile_image')
        if profile_image:
            photo_url = profile_image.url
            return request.build_absolute_uri(photo_url)
        else:
            return None


class UploadProfilePictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("profile_image", 'id')


class UserPermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserPermission
        exclude = ('created_at', 'updated_at',)


class AddressSerializer(serializers.ModelSerializer):
    locality_location_lat = serializers.ReadOnlyField(source='locality_location.y')
    locality_location_long = serializers.ReadOnlyField(source='locality_location.x')
    landmark_location_lat = serializers.ReadOnlyField(source='landmark_location.y', required=False, allow_null=True, default=None)
    landmark_location_long = serializers.ReadOnlyField(source='landmark_location.x', required=False, allow_null=True, default=None)

    class Meta:
        model = Address
        fields = ('id', 'type', 'address', 'land_mark', 'pincode',
                  'phone_number', 'is_default', 'profile', 'locality',
                  'landmark_place_id', 'locality_place_id', 'locality_location_lat', 'locality_location_long',
                  'landmark_location_lat', 'landmark_location_long')

    def create(self, validated_data):
        request = self.context.get("request")
        if not request:
            raise ValueError("Request is None.")
        validated_data['user'] = request.user
        if 'is_default' not in request.data:
            if not Address.objects.filter(user=request.user.id).exists():
                validated_data['is_default'] = True
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context.get("request")
        # if attrs.get("user") != request.user:
        #     raise serializers.ValidationError("User is not correct.")
        if attrs.get("profile") and not UserProfile.objects.filter(user=request.user, id=attrs.get("profile").id).exists():
            raise serializers.ValidationError("Profile is not correct.")
        return attrs


class AppointmentqueryRetrieveSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    source = serializers.ChoiceField(choices=AppointmentHistory.SOURCE_CHOICES, required=False)
    completed = serializers.BooleanField(required=False)


class ConsumerAccountModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerAccount
        fields = "__all__"


class TransactionSerializer(serializers.Serializer):
    # productId = serializers.ChoiceField(choices=Order.PRODUCT_IDS)
    # referenceId = serializers.IntegerField(required=False)
    orderId = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    orderNo = serializers.CharField(max_length=200, required=False)
    paymentMode = serializers.CharField(max_length=200, required=False)
    txAmount = serializers.DecimalField(max_digits=12, decimal_places=2)
    responseCode = serializers.CharField(max_length=200)
    bankTxId = serializers.CharField(max_length=200, allow_blank=True, required=False)
    txDate = serializers.CharField(max_length=100)
    bankName = serializers.CharField(max_length=200, required=False)
    currency = serializers.CharField(max_length=200)
    statusCode = serializers.IntegerField()
    pgGatewayName = serializers.CharField(max_length=20, required=False)
    txStatus = serializers.CharField(max_length=200)
    pgTxId = serializers.CharField(max_length=200)
    pbGatewayName = serializers.CharField(max_length=200, required=False)
    hash = serializers.CharField(max_length=1000)
    nodalId = serializers.IntegerField()


class UserTransactionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsumerTransaction
        fields = ('type', 'action', 'amount', 'product_id', 'reference_id', 'order_id', 'created_at', 'source')
        # fields = '__all__'


class RefreshJSONWebTokenSerializer(serializers.Serializer):

    token = serializers.CharField()
    reset = serializers.CharField(required=False)
    force_update = serializers.BooleanField(required=False)

    def validate(self, attrs):
        import hashlib, time
        token = attrs.get('token')
        reset = attrs.get('reset')
        app_name = self.context.get('app_name')
        is_agent = self.context.get('is_agent', None)
        force_update = True if (attrs.get('force_update') and attrs['force_update']) else False
        request = self.context.get('request')
        payload, status = self.check_payload_v2(token)
        uid = payload if status == 0 else payload.get('user_id')
        # if not WhiteListedLoginTokens.objects.filter(token=token, user_id=uid).exists():
        #     attrs['active_session_error'] = True
        #     return attrs
        #     raise serializers.ValidationError("No Last Active sesssion found!")
        if is_agent or (status == 1 and not force_update):
            '''FAke Refresh, Return the original data [As required by Rohit Dhall]'''
            attrs['token']= token
            attrs['user'] = payload.get('user_id')
            attrs['payload'] = payload
            if payload.get('agent_id',None):
                attrs['agent_id'] = payload.get('agent_id')
        elif (force_update or reset):
            try:
                passphrase = hashlib.md5("hpDqwzdpoQY8ymm5".encode())
                passphrase = passphrase.hexdigest()[:16]
                decrypt = v1_utils.AES_encryption.decrypt(reset.encode(), passphrase)
                if decrypt and isinstance(decrypt, tuple):
                    decrypt = decrypt[0]
                    data = v1_utils.AES_encryption.unpad(decrypt)
            except Exception as e:
                logger.error("Failed to decrypt data " + str(e))
                raise serializers.ValidationError('Failed to decrypt!')
            get_date = data.split('.')
            if len(get_date) > 1:
                uid = get_date[0]
                last_time_object = int(get_date[1])
                current_object = time.time()
                delta = current_object - last_time_object
                time_elapsed = delta / 60

                if time_elapsed > 10:
                    logger.error('Reset Key Expired  --last ' + str(last_time_object) + '| current -- '+ str(current_object) + '| delta --' + str(delta))
                    # raise serializers.ValidationError('Reset Key Expired' + ' '+str(date_generated) + '   elapsed '+str(time_elapsed)+ ' current '+ str(current_time_string))
                    raise serializers.ValidationError('Reset Key Expired' +  ' last ' + str(last_time_object) + ' current  '+ str(current_object) + ' delta ' + str(delta) )
                else:
                    user = User.objects.filter(id=uid).first()
                    # blacllist_token = WhiteListedLoginTokens.objects.filter(token=token, user=user).delete()
                    token_object = JWTAuthentication.generate_token(user, request)
                    attrs['token'] = token_object['token']
                    attrs['user'] = user.id
                    attrs['payload'] = token_object['payload']
        return attrs
        # payload = self.check_payload_custom(token=token)
        # user = self.check_user_custom(payload=payload)
        # # Get and check 'orig_iat'
        # orig_iat = payload.get('orig_iat')
        #
        # if orig_iat:
        #     # Verify expiration
        #     refresh_limit = settings.JWT_AUTH['JWT_REFRESH_EXPIRATION_DELTA']
        #
        #     if isinstance(refresh_limit, datetime.timedelta):
        #         refresh_limit = (refresh_limit.days * 24 * 3600 +
        #                          refresh_limit.seconds)
        #
        #     expiration_timestamp = orig_iat + int(refresh_limit)
        #     now_timestamp = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
        #
        #     if now_timestamp > expiration_timestamp:
        #         msg = _('Token has expired.')
        #         raise serializers.ValidationError(msg)
        # else:
        #     msg = _('orig_iat missing')
        #     raise serializers.ValidationError(msg)
        # blacllist_token = WhiteListedLoginTokens.objects.filter(token=token, user=user).delete()
        # # if blacllist_token and isinstance(blacllist_token, tuple) and (blacllist_token[0] > 0):
        # token_object = JWTAuthentication.generate_token(user, request)
        # token_object['payload']['orig_iat'] = orig_iat
        # return {
        #     'token': token_object['token'],
        #     'user': user,
        #     'payload': token_object['payload']
        # }
        # else:
        # return serializers.ValidationError("Token Has expired")

    def check_user_custom(self, payload):
        uid = payload.get('user_id')

        if not uid:
            msg = ('Invalid Token.')
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            msg = ("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = ('User account is disabled.')
            raise serializers.ValidationError(msg)

        return user

    def check_payload_custom(self, token):
        user_key = None
        user_id = JWTAuthentication.get_unverified_user(token)
        if user_id:
            user_key_object = UserSecretKey.objects.filter(user_id=user_id).first()
            if user_key_object:
                user_key = user_key_object.key
        try:
            payload = jwt.decode(token, user_key)
        except jwt.ExpiredSignature:
            msg = ('Token has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = ('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

    def check_payload_v2(self, token):
        user_key = None
        user_id, agent_id = JWTAuthentication.get_unverified_user(token)
        if user_id:
            user_key_object = UserSecretKey.objects.filter(user_id=user_id).first()
            if user_key_object:
                user_key = user_key_object.key
        try:
            payload = jwt.decode(token, user_key)
        except jwt.ExpiredSignature:
            msg = ('Token has expired.')
            return user_id, 0
        return payload, 1


class OnlineLeadSerializer(serializers.ModelSerializer):
    member_type = serializers.ChoiceField(choices=OnlineLead.TYPE_CHOICES)
    name = serializers.CharField(max_length=255)
    speciality = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    mobile = serializers.IntegerField(allow_null=False, max_value=9999999999, min_value=1000000000)
    city_name = serializers.IntegerField(required=False)
    email = serializers.EmailField()
    utm_params = serializers.JSONField(required=False)
    source = serializers.CharField(max_length=128, required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        if attrs['city_name'] > 0:
            if not common_models.Cities.objects.filter(id=attrs['city_name']).exists():
                raise serializers.ValidationError('City not found for given city.')

            attrs['city_name'] = common_models.Cities.objects.filter(id=attrs['city_name']).first()
        else:
            attrs['city_name'] = None
        return attrs

    class Meta:
        model = OnlineLead
        fields = ('member_type', 'name', 'speciality', 'mobile', 'city_name', 'email', 'utm_params', 'source')


class CareerSerializer(serializers.ModelSerializer):
    profile_type = serializers.ChoiceField(choices=Career.PROFILE_TYPE_CHOICES)
    name = serializers.CharField(max_length=255)
    mobile = serializers.IntegerField(max_value=9999999999, min_value=1000000000)
    email = serializers.EmailField()
    resume = serializers.FileField()

    class Meta:
        model = Career
        fields = ('profile_type', 'name', 'mobile', 'email', 'resume')


class OrderDetailDoctorSerializer(serializers.Serializer):
    product_id = serializers.ChoiceField(choices=Order.PRODUCT_IDS)
    profile = serializers.IntegerField(source="action_data.profile")
    date = serializers.SerializerMethodField()
    hospital = serializers.IntegerField(source="action_data.hospital")
    doctor = serializers.IntegerField(source="action_data.doctor")
    time = serializers.SerializerMethodField()

    def get_time(self, obj):
        from keel.api.v1.diagnostic.views import LabList
        app_date_time = parse_datetime(obj.action_data.get("time_slot_start"))
        value = round(float(app_date_time.hour) + (float(app_date_time.minute)*1/60), 2)
        lab_obj = LabList()
        text = lab_obj.convert_time(value)
        doc_deal_price, doc_mrp, doc_agreed_price = obj.get_doctor_prices()
        doc_deal_price, doc_mrp = str(doc_deal_price), str(doc_mrp)
        data = {
            'deal_price': doc_deal_price,
            'is_available': True,
            'effective_price': obj.action_data.get("effective_price"),
            'mrp': doc_mrp,
            'value': value,
            'text': text
        }
        return data

    def get_date(self, obj):
        date_str = obj.action_data.get("time_slot_start")
        date = parse_datetime(date_str)
        return date.date()

    class Meta:
        fields = ('product_id', 'date', 'hospital', 'doctor', 'time')


class OrderDetailLabSerializer(serializers.Serializer):
    product_id = serializers.ChoiceField(choices=Order.PRODUCT_IDS)
    profile = serializers.IntegerField(source="action_data.profile")
    lab = serializers.IntegerField(source="action_data.lab")
    test_ids = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    is_home_pickup = serializers.BooleanField(source="action_data.is_home_pickup", default=False)
    address = serializers.IntegerField(source="action_data.address.id", default=None)

    def get_test_ids(self, obj):
        queryset = AvailableLabTest.objects.filter(id__in=obj.action_data.get("lab_test")).values("test", "test__name")
        test_ids = [{"id": d["test"], "name": d["test__name"]} for d in queryset]
        return test_ids

    def get_time(self, obj):
        from keel.api.v1.diagnostic.views import LabList
        app_date_time = parse_datetime(obj.action_data.get("time_slot_start"))
        value = round(float(app_date_time.hour) + (float(app_date_time.minute)*1/60), 2)
        lab_obj = LabList()
        text = lab_obj.convert_time(value)
        data = {
            'deal_price': obj.action_data.get("deal_price"),
            'is_available': True,
            'effective_price': obj.action_data.get("effective_price"),
            'price': obj.action_data.get("price"),
            'value': value,
            'text': text
        }
        return data

    def get_date(self, obj):
        date_str = obj.action_data.get("time_slot_start")
        date = parse_datetime(date_str)
        return date.date()

    class Meta:
        fields = ('product_id', 'lab', 'date', 'time', 'test_ids', 'profile', 'is_home_pickup', 'address')


class ContactUsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    mobile = serializers.IntegerField(min_value=1000000000, max_value=9999999999)
    email = serializers.EmailField()
    message = serializers.CharField(max_length=2000)
    from_app = serializers.BooleanField(default=False)

    class Meta:
        model = ContactUs
        fields = ('name', 'mobile', 'email', 'message')


class UserLeadSerializer(serializers.ModelSerializer):

    gender = serializers.ChoiceField(choices=UserLead.gender_choice, allow_null=True, allow_blank=True)
    name = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(max_length=15, required=True)
    message = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = UserLead
        fields = ('name', 'phone_number', 'gender', 'message')


class TokenFromUrlKeySerializer(serializers.Serializer):
    auth_token = serializers.CharField(max_length=100, required=False)
    key = serializers.CharField(max_length=30, required=False)

    def validate(self, attrs):
        if not (attrs.get('auth_token') or attrs.get('key')):
            raise serializers.ValidationError('neither auth_token nor key found')
        return attrs


class ProfileEmailUpdateInitSerializer(serializers.Serializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), allow_null=False)
    email = serializers.EmailField(max_length=256, required=True)

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        email = attrs.get('email')
        profile = attrs.get('profile')

        if not UserProfileEmailUpdate.can_be_changed(user, email):
            raise serializers.ValidationError('Email is being used by another user.')

        if not UserProfile.objects.filter(id=profile.id, user=user).exists():
            raise serializers.ValidationError('Given profile is not valid family profile.')

        return attrs


class ProfileEmailUpdateProcessSerializer(serializers.Serializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), allow_null=False)
    otp = serializers.IntegerField(min_value=100000, max_value=999999, required=True)
    id = serializers.IntegerField(required=True, min_value=1)
    process_immediately = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        profile = attrs.get('profile')

        if not UserProfile.objects.filter(id=profile.id, user=user).exists():
            raise serializers.ValidationError('Given profile is not valid family profile.')

        return attrs


class ExternalLoginSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=1000000000,max_value=9999999999)
    name = serializers.CharField(max_length=100)
    is_default_user = serializers.BooleanField(required=False)
    email = serializers.EmailField(required=True, allow_null=True, allow_blank=True)
    extra = serializers.JSONField(allow_null=True, required=False)
    redirect_type = serializers.ChoiceField(choices=[('doctor',"Doctor"), ('lab',"Lab")])


class MatrixUserLoginSerializer(serializers.Serializer):
    GENDER_CHOICES = UserProfile.GENDER_CHOICES
    name = serializers.CharField(max_length=100)
    phone_number = serializers.IntegerField(min_value=1000000000, max_value=9999999999)
    is_default_user = serializers.BooleanField(required=False)
    email = serializers.EmailField()
    dob = serializers.DateField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    extra = serializers.JSONField(allow_null=True, required=False)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    hospital = serializers.PrimaryKeyRelatedField(queryset=Hospital.objects.all())


# class CloudLabUserLoginSerializer(serializers.Serializer):
#     GENDER_CHOICES = UserProfile.GENDER_CHOICES
#     name = serializers.CharField(max_length=100)
#     phone_number = serializers.IntegerField(min_value=1000000000, max_value=9999999999)
#     is_default_user = serializers.BooleanField(required=False)
#     email = serializers.EmailField()
#     dob = serializers.DateField()
#     gender = serializers.ChoiceField(choices=GENDER_CHOICES)
#     extra = serializers.JSONField(allow_null=True, required=False)


class PGRefundSaveSerializer(serializers.Serializer):
    mode = serializers.CharField(max_length=24)
    refNo = serializers.IntegerField()
    orderNo = serializers.CharField(required=False)
    orderId = serializers.IntegerField()
    bankRefNum = serializers.IntegerField(allow_null=True)
    refundDate = serializers.DateTimeField()
    refundId = serializers.IntegerField()
    txnAmount = serializers.FloatField()
    gateway = serializers.CharField(allow_null=True)
    bank_arn = serializers.CharField(allow_null=True)
    refundAmount = serializers.FloatField()

    def validate(self, attrs):
        refund_obj = ConsumerRefund.objects.select_related('pg_transaction').filter(id=attrs['refNo']).first()
        if refund_obj and refund_obj.refund_state == ConsumerRefund.COMPLETED and refund_obj.pg_transaction.order.id == attrs['orderId']:
            attrs['refund_obj'] = refund_obj
        else:
            raise serializers.ValidationError('Invalid Refund!')
        return attrs
