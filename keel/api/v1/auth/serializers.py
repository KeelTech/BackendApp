from rest_framework import serializers
from keel.authentication.models import (User, UserDocument, CustomerWorkExperience, WorkExperienceLabel,
                                        CustomerProfile,  CustomerProfileLabel, QualificationLabel, CustomerQualifications,
                                        RelativeInCanada, RelativeInCanadaLabel, EducationalCreationalAssessment, 
                                        EducationalCreationalAssessmentLabel)
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
    phone_number = serializers.SerializerMethodField()
    class Meta:
        model = CustomerProfile
        fields = ('id', 'first_name', 'last_name', 'mother_fullname', 
                    'father_fullname', 'age', 'address', 'date_of_birth', 'phone_number')
    
    def get_phone_number(self, obj):
        phone_number = obj.user.phone_number
        return phone_number


class CustomerProfileLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    mother_fullname = serializers.SerializerMethodField()
    father_fullname = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_first_name(self, obj):
        var = obj.first_name
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["first_name_label"]}

    def get_last_name(self, obj):
        var = obj.last_name
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["last_name_label"]}

    def get_mother_fullname(self, obj):
        var = obj.mother_fullname
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["mother_fullname_label"]}

    def get_father_fullname(self, obj):
        var = obj.father_fullname
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["father_fullname_label"]}

    def get_age(self, obj):
        var = obj.age
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["age_label"]}

    def get_address(self, obj):
        var = obj.address
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["address_label"]}

    def get_date_of_birth(self, obj):
        var = obj.date_of_birth
        if "labels" in self.context:
            return {"value": var, "type":"calendar", "labels":self.context["labels"]["date_of_birth_label"]}

    class Meta:
        model = CustomerProfileLabel
        fields = ('first_name', 'last_name', 'mother_fullname', 
                    'father_fullname', 'age', 'address', 'date_of_birth', 'labels')


class CustomerQualificationsSerializer(serializers.ModelSerializer):
    institute = serializers.CharField(required=True)
    grade = serializers.CharField(required=True)
    year_of_passing = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    class Meta:
        model = CustomerQualifications
        fields = ('id', 'institute', 'grade', 'year_of_passing', 'start_date', 
                    'end_date', 'city', 'country')

class CustomerQualificationsLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()
    year_of_passing = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_institute(self, obj):
        var = obj.institute
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["institute_label"]}
    
    def get_year_of_passing(self, obj):
        var = obj.year_of_passing 
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["year_of_passing_label"]}
    
    def get_city(self, obj):
        var = obj.city
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["city_label"]}
    
    def get_country(self, obj):
        var = obj.country
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["country_label"]}
    
    def get_start_date(self, obj):
        var = obj.start_date
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["start_date_label"]}
        
    def get_end_date(self, obj):
        var = obj.end_date
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["end_date_label"]}
    
    class Meta:
        model = QualificationLabel
        fields = ('id', 'institute', 'year_of_passing', 'city', 'country',
                    'start_date', 'end_date', 'labels')


class CustomerWorkExperienceSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    job_type = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)
    job_description = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    weekly_working_hours = serializers.CharField(required=True)
    class Meta:
        model = CustomerWorkExperience
        fields = ('id', 'job_type', 'designation', 'job_description', 'company_name',
                    'city', 'weekly_working_hours', 'start_date', 'end_date')
                    

class WorkExperienceLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    job_description = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    weekly_working_hours = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_job_type(self, obj):
        var = obj.job_type
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["job_type_label"]}

    def get_designation(self, obj):
        var = obj.designation
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["designation_label"]}

    def get_start_date(self, obj):
        var = obj.start_date
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["start_date_label"]}

    def get_end_date(self, obj):
        var = obj.end_date
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["end_date_label"]}

    def get_job_description(self, obj):
        var = obj.job_description
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["job_description_label"]}
            
    def get_company_name(self, obj):
        var = obj.company_name
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["company_name_label"]}

    def get_city(self, obj):
        var = obj.city
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["city_label"]}

    def get_weekly_working_hours(self, obj):
        var = obj.weekly_working_hours
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["weekly_working_hours_label"]}
    
    class Meta:
        model = WorkExperienceLabel
        fields = ('id', 'company_name', 'start_date', 'end_date', 'city', 'weekly_working_hours', 
                    'designation', 'job_type', 'labels', 'job_description')

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


class RelativeInCanadaSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    relationship = serializers.CharField(required=True)
    immigration_status = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    contact_number = serializers.CharField(required=True)
    email_address = serializers.CharField(required=True)
    class Meta:
        model = RelativeInCanada
        fields = ('id', 'full_name', 'relationship', 'immigration_status', 
                    'address', 'contact_number', 'email_address')


class RelativeInCanadaLabelSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    relationship = serializers.SerializerMethodField()
    immigrations_status = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    email_address = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_full_name(self, obj):
        var = obj.full_name
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["full_name_label"]}

    def get_relationship(self, obj):
        var = obj.relationship
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["relationship_label"]}

    def get_immigrations_status(self, obj):
        var = obj.immigration_status
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["immigrations_status_label"]}

    def get_address(self, obj):
        var = obj.address
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["address_label"]}

    def get_contact_number(self, obj):
        var = obj.contact_number
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["contact_number_label"]}

    def get_email_address(self, obj):
        var = obj.email_address
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["email_address_label"]}

    class Meta:
        model = RelativeInCanadaLabel
        fields = ('id', 'full_name', 'relationship', 'immigrations_status', 'address', 
                    'contact_number', 'email_address')


class EducationalCreationalAssessmentSerializer(serializers.ModelSerializer):
    eca_authority_name = serializers.CharField(required=True)
    eca_authority_number = serializers.CharField(required=True)
    canadian_equivalency_summary = serializers.CharField(required=True)

    class Meta:
        model = EducationalCreationalAssessment
        fields = ('id', 'eca_authority_name', 'eca_authority_number', 'canadian_equivalency_summary')


class EducationalCreationalAssessmentLabelSerializer(serializers.ModelSerializer):
    eca_authority_name = serializers.SerializerMethodField()
    eca_authority_number = serializers.SerializerMethodField()
    canadian_equivalency_summary = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_eca_authority_name(self, obj):
        var = obj.eca_authority_name
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["eca_authority_name_label"]}

    def get_eca_authority_number(self, obj):
        var = obj.eca_authority_number
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["eca_authority_number_label"]}

    def get_canadian_equivalency_summary(self, obj):
        var = obj.canadian_equivalency_summary
        if "labels" in self.context:
            return {"value": var, "type":"char", "labels":self.context["labels"]["canadian_equivalency_summary_label"]}

    class Meta:
        model = EducationalCreationalAssessmentLabel
        fields = ('id', 'eca_authority_name', 'eca_authority_number', 'canadian_equivalency_summary')