import logging

from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from keel.api.v1 import utils as v1_utils
from keel.authentication.models import (
    AgentProfile,
    CustomerProfile,
    CustomerProfileLabel,
    CustomerQualifications,
    CustomerWorkExperience,
    EducationalCreationalAssessment,
    EducationalCreationalAssessmentLabel,
    QualificationLabel,
    RelativeInCanada,
    RelativeInCanadaLabel,
    SMSOtpModel,
    User,
    UserDocument,
    WorkExperienceLabel,
)
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error, logging_format
from rest_framework import serializers

# from keel.common import models as common_models

logger = logging.getLogger("app-logger")


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "user_type",
            "is_active",
            "is_verified",
            "date_joined",
        )


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)


class BaseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        exclude = ("created_at", "updated_at", "deleted_at")


class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        exclude = ("created_at", "updated_at", "deleted_at")


class InitialProfileSerializer(BaseProfileSerializer):
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = CustomerProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "current_country",
            "phone_number",
            "desired_country",
            "age",
        )

    def create(self, validated_data):
        profile = CustomerProfile.objects.create(**validated_data)
        return profile


class CustomerProfileSerializer(BaseProfileSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    mother_fullname = serializers.CharField(required=True)
    father_fullname = serializers.CharField(required=True)
    age = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.SerializerMethodField()
    current_country = serializers.SerializerMethodField()
    desired_country = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "mother_fullname",
            "current_country",
            "desired_country",
            "father_fullname",
            "age",
            "address",
            "date_of_birth",
            "phone_number",
        )

    def get_phone_number(self, obj):
        phone_number = obj.user.phone_number
        return phone_number


class CustomerUpdateProfileSerializer(BaseProfileSerializer):
    class Meta:
        model = CustomerProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "mother_fullname",
            "current_country",
            "desired_country",
            "father_fullname",
            "age",
            "address",
            "date_of_birth",
        )

    def create(self, validated_data):
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        mother_fullname = validated_data.get("mother_fullname")
        father_fullname = validated_data.get("father_fullname")
        age = validated_data.get("age")
        address = validated_data.get("address")
        current_country = validated_data.get("current_country")
        desired_country = validated_data.get("desired_country")
        date_of_birth = validated_data.get("date_of_birth")
        user = validated_data.get("user")
        try:
            profile = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist as err:
            logger.error(
                logging_format(
                    LOGGER_LOW_SEVERITY, "CustomerUpdateProfileSerializer:create"
                ),
                "",
                description=str(err),
            )
            raise serializers.ValidationError("No profile for this user")
        profile.first_name = first_name
        profile.last_name = last_name
        profile.mother_fullname = mother_fullname
        profile.father_fullname = father_fullname
        profile.age = age
        profile.address = address
        profile.current_country = current_country
        profile.desired_country = desired_country
        profile.date_of_birth = date_of_birth
        profile.save()
        return profile


class CustomerProfileLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    mother_fullname = serializers.SerializerMethodField()
    father_fullname = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    current_country = serializers.SerializerMethodField()
    desired_country = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_first_name(self, obj):
        var = obj.first_name
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["first_name_label"],
            }

    def get_last_name(self, obj):
        var = obj.last_name
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["last_name_label"],
            }

    def get_mother_fullname(self, obj):
        var = obj.mother_fullname
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["mother_fullname_label"],
            }

    def get_father_fullname(self, obj):
        var = obj.father_fullname
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["father_fullname_label"],
            }

    def get_age(self, obj):
        var = obj.age
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["age_label"],
            }

    def get_address(self, obj):
        var = obj.address
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["address_label"],
            }

    def get_date_of_birth(self, obj):
        var = obj.date_of_birth
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["date_of_birth_label"],
            }

    def get_phone_number(self, obj):
        var = obj.user.phone_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["phone_number_label"],
            }

    def get_current_country(self, obj):
        if obj.current_country is not None:
            var = obj.current_country.id
            name = obj.current_country.name
            if "labels" in self.context:
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["current_country_label"],
                }

    def get_desired_country(self, obj):
        if obj.desired_country is not None:
            var = obj.desired_country.id
            name = obj.desired_country.name
            if "labels" in self.context:
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["desired_country_label"],
                }

    class Meta:
        model = CustomerProfileLabel
        fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "age",
            "phone_number",
            "mother_fullname",
            "father_fullname",
            "current_country",
            "desired_country",
            "address",
            "labels",
        )


class CustomerQualificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQualifications
        fields = (
            "id",
            "institute",
            "degree",
            "grade",
            "year_of_passing",
            "start_date",
            "end_date",
            "city",
            "country",
            "state",
        )


class CustomerQualificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQualifications
        fields = (
            "id",
            "institute",
            "degree",
            "grade",
            "year_of_passing",
            "start_date",
            "end_date",
            "city",
            "country",
            "state",
        )


class CustomerQualificationsLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    year_of_passing = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_institute(self, obj):
        var = obj.institute
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["institute_label"],
            }

    def get_degree(self, obj):
        var = obj.degree
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["degree_label"],
            }

    def get_grade(self, obj):
        var = obj.grade
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["grade_label"],
            }

    def get_year_of_passing(self, obj):
        var = obj.year_of_passing
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["year_of_passing_label"],
            }

    def get_country(self, obj):
        if "labels" in self.context:
            if obj.country:
                var = obj.country.id
                name = obj.country.name
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["country_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["country_label"],
            }

    def get_state(self, obj):
        if "labels" in self.context:
            if obj.state:
                var = obj.state.id
                name = obj.state.state
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["state_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["state_label"],
            }

    def get_city(self, obj):
        if "labels" in self.context:
            if obj.city:
                var = obj.city.id
                name = obj.city.city_name
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["city_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["city_label"],
            }

    def get_full_address(self, obj):
        if "labels" in self.context:
            if obj.country != None and obj.city != None and obj.state != None:
                country, state, city = obj.country, obj.state, obj.city
                return {
                    "type": "address",
                    "countryLabel": self.context["labels"]["country_label"],
                    "country": country.name,
                    "countryId": country.id,
                    "stateLabel": self.context["labels"]["state_label"],
                    "state": state.state,
                    "stateId": state.id,
                    "cityLabel": self.context["labels"]["city_label"],
                    "city": city.city_name,
                    "cityId": city.id,
                }
            return {
                "type": "address",
                "countryLabel": self.context["labels"]["country_label"],
                "country": "",
                "countryId": "",
                "stateLabel": self.context["labels"]["state_label"],
                "state": "",
                "stateId": "",
                "cityLabel": self.context["labels"]["city_label"],
                "city": "",
                "cityId": "",
            }

    def get_start_date(self, obj):
        var = obj.start_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["start_date_label"],
            }

    def get_end_date(self, obj):
        var = obj.end_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["end_date_label"],
            }

    class Meta:
        model = QualificationLabel
        fields = (
            "id",
            "institute",
            "year_of_passing",
            "degree",
            "grade",
            "country",
            "state",
            "city",
            "start_date",
            "end_date",
            "labels",
            "full_address",
        )


class CustomerWorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerWorkExperience
        fields = (
            "id",
            "job_type",
            "designation",
            "job_description",
            "company_name",
            "city",
            "state",
            "country",
            "weekly_working_hours",
            "start_date",
            "end_date",
        )


class CustomerUpdateWorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerWorkExperience
        fields = (
            "id",
            "job_type",
            "designation",
            "job_description",
            "company_name",
            "country",
            "state",
            "city",
            "weekly_working_hours",
            "start_date",
            "end_date",
        )


class WorkExperienceLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    job_description = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    weekly_working_hours = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_job_type(self, obj):
        var = obj.job_type
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["job_type_label"],
            }

    def get_designation(self, obj):
        var = obj.designation
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["designation_label"],
            }

    def get_start_date(self, obj):
        var = obj.start_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["start_date_label"],
            }

    def get_end_date(self, obj):
        var = obj.end_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["end_date_label"],
            }

    def get_job_description(self, obj):
        var = obj.job_description
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["job_description_label"],
            }

    def get_company_name(self, obj):
        var = obj.company_name
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["company_name_label"],
            }

    def get_country(self, obj):
        if "labels" in self.context:
            if obj.country:
                var = obj.country.id
                name = obj.country.name
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["country_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["country_label"],
            }

    def get_state(self, obj):
        if "labels" in self.context:
            if obj.state:
                var = obj.state.id
                name = obj.state.state
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["state_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["state_label"],
            }

    def get_city(self, obj):
        if "labels" in self.context:
            if obj.city:
                var = obj.city.id
                name = obj.city.city_name
                return {
                    "value": var,
                    "name": name,
                    "type": "drop-down",
                    "labels": self.context["labels"]["city_label"],
                }
            return {
                "value": "",
                "type": "drop-down",
                "labels": self.context["labels"]["city_label"],
            }

    def get_full_address(self, obj):
        if "labels" in self.context:
            if obj.country != None and obj.city != None and obj.state != None:
                country, state, city = obj.country, obj.state, obj.city
                return {
                    "type": "address",
                    "countryLabel": self.context["labels"]["country_label"],
                    "country": country.name,
                    "countryId": country.id,
                    "stateLabel": self.context["labels"]["state_label"],
                    "state": state.state,
                    "stateId": state.id,
                    "cityLabel": self.context["labels"]["city_label"],
                    "city": city.city_name,
                    "cityId": city.id,
                }
            return {
                "type": "address",
                "countryLabel": self.context["labels"]["country_label"],
                "country": "",
                "countryId": "",
                "stateLabel": self.context["labels"]["state_label"],
                "state": "",
                "stateId": "",
                "cityLabel": self.context["labels"]["city_label"],
                "city": "",
                "cityId": "",
            }

    def get_weekly_working_hours(self, obj):
        var = obj.weekly_working_hours
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["weekly_working_hours_label"],
            }

    class Meta:
        model = WorkExperienceLabel
        fields = (
            "id",
            "company_name",
            "designation",
            "job_type",
            "job_description",
            "weekly_working_hours",
            "start_date",
            "end_date",
            "country",
            "state",
            "city",
            "full_address",
            "labels",
        )


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)

        # get insensitive email match
        user = User.objects.filter(email__iexact=email).first()

        if not user:
            raise serializers.ValidationError("Invalid Credentials, Try Again")
        
        check_password = user.check_password(password)
        
        # check password
        if not check_password:
            raise serializers.ValidationError("Invalid Credentials, Try Again")

        if not user.is_active:
            raise serializers.ValidationError(
                "User is not active. Contact Administrator"
            )

        # check user type
        if user.user_type != user.CUSTOMER:
            raise serializers.ValidationError("Not a customer account")

        return user


class AgentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email", None)
        password = attrs.get("password", None)

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid Credentials, Try Again")

        if not user.is_active:
            raise serializers.ValidationError(
                "User is not active. Contact Administrator"
            )

        # check user type
        types = [user.RCIC, user.ACCOUNT_MANAGER]
        if user.user_type not in types:
            raise serializers.ValidationError("Not an agent account")

        return user


class UserSocialLoginSerializer(SocialLoginSerializer):
    user = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs["user"]
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


class OTPSerializer(serializers.ModelSerializer):
    phone_number = serializers.IntegerField(min_value=5000000000, max_value=9999999999)
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

    class Meta:
        model = SMSOtpModel
        fields = "__all__"


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    # token = serializers.CharField()


class UserDocumentSerializer(serializers.ModelSerializer):
    doc_type = serializers.SerializerMethodField()

    def get_doc_type(self, obj):
        return obj.doc.doc_type.doc_type_name

    class Meta:
        model = UserDocument
        fields = ("id", "doc", "user", "task", "doc_type", "created_at")

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
            user = User.objects.get(id=user_id)
        except Exception as e:
            log_error(
                "ERROR",
                "ListUserDocumentSerializer: get_user_type",
                str(user_id),
                err=str(e),
            )
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
        fields = (
            "id",
            "doc_id",
            "user_id",
            "doc_type",
            "task",
            "orignal_file_name",
            "created_at",
            "user_type",
        )


class UserDetailsSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    # def get_user_name(self, obj):
    #     email = obj.email
    #     username = ''
    #     try:
    #         username = email.split("@")[0]
    #     except Exception as e:
    #         log_error("ERROR", "UserDetailsSerializer: get_user_name","", err = str(e), email = email)
    #     return username

    def get_user_name(self, obj):
        try:
            return obj.user_profile.get_user_name
        except:
            return ""

    class Meta:
        model = User
        fields = ("id", "user_name", "email")


class TaskIDSerializer(serializers.Serializer):

    task_id = serializers.CharField(max_length=255)

    def validate(self, attrs):
        from keel.tasks.models import Task

        task_id = attrs.get("task_id")
        try:
            task = Task.objects.get(pk=task_id, deleted_at__isnull=True)
        except Task.DoesNotExist as e:
            log_error(
                "ERROR", "TaskIDSerializer: validate", "", err=str(e), task_id=task_id
            )
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
        fields = (
            "id",
            "full_name",
            "relationship",
            "immigration_status",
            "address",
            "contact_number",
            "email_address",
            "is_blood_relationship",
        )


class RelativeInCanadaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelativeInCanada
        fields = (
            "id",
            "full_name",
            "relationship",
            "immigration_status",
            "address",
            "contact_number",
            "email_address",
            "is_blood_relationship",
        )

    def create(self, validated_data):
        id = validated_data.get("id")
        full_name = validated_data.get("full_name")
        relationship = validated_data.get("relationship")
        immigration_status = validated_data.get("immigration_status")
        address = validated_data.get("address")
        contact_number = validated_data.get("contact_number")
        email_address = validated_data.get("email_address")
        is_blood_relationship = validated_data.get("is_blood_relationship")
        user = validated_data.get("user")
        try:
            relative, created = RelativeInCanada.objects.update_or_create(
                id=id,
                defaults={
                    "full_name": full_name,
                    "relationship": relationship,
                    "immigration_status": immigration_status,
                    "address": address,
                    "contact_number": contact_number,
                    "email_address": email_address,
                    "is_blood_relationship": is_blood_relationship,
                    "user": user,
                },
            )
        except RelativeInCanada.DoesNotExist as err:
            logger.error(
                logging_format(
                    LOGGER_LOW_SEVERITY, "RelativeInCanadaUpdateSerializer:create"
                ),
                "",
                description=str(err),
            )
            raise serializers.ValidationError("Relative with ID does not exist")

        return relative


class RelativeInCanadaLabelSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    relationship = serializers.SerializerMethodField()
    immigration_status = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    email_address = serializers.SerializerMethodField()
    is_blood_relationship = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_full_name(self, obj):
        var = obj.full_name
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["full_name_label"],
            }

    def get_relationship(self, obj):
        var = obj.relationship
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["relationship_label"],
            }

    def get_immigration_status(self, obj):
        var = obj.immigration_status
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["immigration_status_label"],
            }

    def get_address(self, obj):
        var = obj.address
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["address_label"],
            }

    def get_contact_number(self, obj):
        var = obj.contact_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["contact_number_label"],
            }

    def get_is_blood_relationship(self, obj):
        var = obj.is_blood_relationship
        if "labels" in self.context:
            return {
                "value": var,
                "type": "checkbox",
                "lables": self.context["labels"]["is_blood_relationship_label"],
            }

    def get_email_address(self, obj):
        var = obj.email_address
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["email_address_label"],
            }

    class Meta:
        model = RelativeInCanadaLabel
        fields = (
            "id",
            "full_name",
            "relationship",
            "immigration_status",
            "address",
            "contact_number",
            "email_address",
            "is_blood_relationship",
        )


class EducationalCreationalAssessmentSerializer(serializers.ModelSerializer):
    eca_authority_name = serializers.CharField(required=True)
    eca_authority_number = serializers.CharField(required=True)
    canadian_equivalency_summary = serializers.CharField(required=True)

    class Meta:
        model = EducationalCreationalAssessment
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
        )


class EducationalCreationalAssessmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalCreationalAssessment
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
        )


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
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["eca_authority_name_label"],
            }

    def get_eca_authority_number(self, obj):
        var = obj.eca_authority_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["eca_authority_number_label"],
            }

    def get_canadian_equivalency_summary(self, obj):
        var = obj.canadian_equivalency_summary
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["canadian_equivalency_summary_label"],
            }

    class Meta:
        model = EducationalCreationalAssessmentLabel
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
        )
