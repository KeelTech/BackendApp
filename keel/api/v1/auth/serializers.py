from rest_framework import serializers
from keel.authentication.models import (User, UserDocument, CustomerWorkExperience, 
                                        CustomerProfile, CustomerQualifications)
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
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    mother_fullname = serializers.CharField(required=True)
    father_fullname = serializers.CharField(required=True)
    age = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)

    class Meta:
        model = CustomerProfile
        fields = ('first_name', 'last_name', 'mother_fullname', 
                    'father_fullname', 'age', 'address', 'date_of_birth')

class CustomerQualificationsSerializer(serializers.ModelSerializer):
    institute_name = serializers.CharField(required=True)
    grade = serializers.CharField(required=True)
    year_of_passing = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        model = CustomerQualifications
        fields = ('id', 'institute_name', 'grade', 'year_of_passing', 'start_date', 
                    'end_date', 'city', 'country')


class CustomerWorkExperienceSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    job_type = serializers.CharField(required=True)
    designation = serializers.DateField(required=True)
    job_description = serializers.DateField(required=True)
    company_name = serializers.DateField(required=True)
    city = serializers.DateField(required=True)
    weekly_working_hours = serializers.DateField(required=True)
    class Meta:
        model = CustomerWorkExperience
        fields = ('id', 'job_type', 'designation', 'job_description', 'company_name',
                    'city', 'weekly_working_hours', 'start_date', 'end_date')


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
    task = serializers.SerializerMethodField()
    orignal_file_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    # doc_link = serializers.SerializerMethodField()

    def get_doc_type(self, obj):
        return obj.doc.doc_type.doc_type_name

    def get_orignal_file_name(self, obj):
        return obj.doc.original_name

    def get_user_type(self, obj):
        user_id = obj.doc.owner_id
        try:
            user = User.objects.get(id = user_id)
        except Exception as e:
            log_error("ERROR", "ListUserDocumentSerializer: get_user_type",str(user_id), err = str(e))
            return dict(User.USER_TYPE_CHOICES).get(User.CUSTOMER)
        return user.get_user_type_display()

    # def get_doc_link(self, obj):
    #     return settings.BASE_URL + "/api/v1/doc/get-single-doc" + "/" +str(obj.doc.doc_pk)

    def get_task(self, obj):
        task = ""
        if obj.task and not obj.task.deleted_at:
            task = obj.task_id
        return task

    class Meta:
        model = UserDocument
        fields = ('id', 'doc_id', 'user_id', 'doc_type','task', 'orignal_file_name', 'created_at','user_type')

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

class TaskIDSerializer(serializers.Serializer):

    task_id = serializers.CharField(max_length=255)

    def validate(self, attrs):
        from keel.tasks.models import Task

        task_id = attrs.get('task_id')
        try:
            task = Task.objects.get(pk = task_id, deleted_at__isnull = True)
        except Task.DoesNotExist as e:
            log_error("ERROR", "TaskIDSerializer: validate", "", err = str(e), task_id = task_id )
            raise serializers.ValidationError("Task Id is invalid")

        return task
