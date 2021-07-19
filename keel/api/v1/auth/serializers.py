from rest_framework import serializers
from keel.authentication.models import (User, UserDocument, CustomToken, CustomerProfile, CustomerQualifications)
from keel.Core.err_log import log_error
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.db.models import Q

from keel.api.v1 import utils as v1_utils
# from keel.common import models as common_models

import logging
logger = logging.getLogger('app-logger')


User = get_user_model()

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)


class CustomerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerProfile
        fields = "__all__"

class CustomerQualificationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerQualifications
        fields = "__all__"


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email', None)
        password = attrs.get('password', None)

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid Credentials, Try Again")

        if not user.is_active:
            raise serializers.ValidationError("User is not active. Contact Administrator")

        return user

class UserSocialLoginSerializer(SocialLoginSerializer):
    user = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']
        if not user.is_active:
            user.is_active = True
            user.save()
        return user

class FacebookSocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField()



class GenerateTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmResetTokenSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

 
class OTPSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(min_value=5000000000,max_value=9999999999)
    via_sms = serializers.BooleanField(default=True, required=False)
    via_whatsapp = serializers.BooleanField(default=False, required=False)
    request_source = serializers.CharField(required=False, max_length=200)

    def validate(self, attrs):
        # otp_obj = OtpVerifications.objects.filter(phone_number=attrs.get('phone_number')).order_by('-id').first()
        # if not attrs.get('via_whatsapp') and otp_obj and not otp_obj.is_expired and (
        #         datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) - v1_utils.aware_time_zone(
        #         otp_obj.updated_at)).total_seconds() < OtpVerifications.TIME_BETWEEN_CONSECUTIVE_REQUESTS:
        #     raise serializers.ValidationError('Please try again in a moment.')
        # if otp_obj:
        #     attrs['otp_obj'] = otp_obj
        return attrs


class UserDocumentSerializer(serializers.ModelSerializer):
    doc_type = serializers.SerializerMethodField()

    def get_doc_type(self, obj):
        return obj.doc.doc_type.doc_type_name

    class Meta:
        model = UserDocument
        fields = ('id', 'doc','user','task','doc_type','created_at')

    def create(self, validated_data):
        user_doc = UserDocument.objects.create(**validated_data)
        return user_doc


class ListUserDocumentSerializer(serializers.ModelSerializer):
    doc_type = serializers.SerializerMethodField()
    # doc_link = serializers.SerializerMethodField()

    def get_doc_type(self, obj):
        return obj.doc.doc_type.doc_type_name

    # def get_doc_link(self, obj):
    #     return settings.BASE_URL + "/api/v1/doc/get-single-doc" + "/" +str(obj.doc.doc_pk)

    class Meta:
        model = UserDocument
        # fields = ('id', 'doc_id', 'user_id', 'doc_link', 'doc_type')
        fields = ('id', 'doc_id', 'user_id', 'doc_type','task','created_at')

class UserDetailsSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        email = obj.email
        username = ''
        try:
            username = email.split("@")[0]
        except Exception as e:
            log_error("ERROR", "UserDetailsSerializer: get_user_name","", err = str(e), email = email)
        return username

    class Meta:
        model = User
        fields = ('id','user_name','email')



