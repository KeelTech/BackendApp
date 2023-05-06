import logging

from dj_rest_auth.registration.serializers import SocialLoginSerializer

from django.contrib.auth import authenticate, get_user_model

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
    User, CustomerFamilyInformation, CustomerFamilyInformationLabel,
    UserDocument, CustomerSpouseProfileLabel, CustomerSpouseProfile,
    WorkExperienceLabel, CustomerLanguageScoreLabel, CustomerLanguageScore,
)
from keel.Core.constants import LOGGER_LOW_SEVERITY, MARITAL_TYPE, VISA_TYPE
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
            # "date_of_birth",
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
            # "date_of_birth",
            "type_of_visa",
            "first_language",
            "city_of_birth",
            "email",
            "marital_status",
            "previous_marriage",
            "height",
            "eye_color",
            "passport_number",
            "passport_country",
            "passport_issue_date",
            "passport_expiry_date",
            "funds_available"
        )

    def create(self, validated_data):

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
        profile.first_name = validated_data.get("first_name")
        profile.last_name = validated_data.get("last_name")
        profile.mother_fullname = validated_data.get("mother_fullname")
        profile.father_fullname = validated_data.get("father_fullname")
        profile.age = validated_data.get("age")
        profile.address = validated_data.get("address")
        profile.current_country = validated_data.get("current_country")
        profile.desired_country = validated_data.get("desired_country")
        # profile.date_of_birth = validated_data.get("date_of_birth")
        profile.type_of_visa = validated_data.get("type_of_visa")

        profile.first_language = validated_data.get("first_language")
        profile.city_of_birth = validated_data.get("city_of_birth")
        profile.email = validated_data.get("email")
        profile.marital_status = validated_data.get("marital_status")
        profile.previous_marriage = validated_data.get("previous_marriage")
        profile.height = validated_data.get("height")
        profile.eye_color = validated_data.get("eye_color")
        profile.funds_available = validated_data.get("funds_available")

        profile.passport_number = validated_data.get("passport_number")
        profile.passport_country = validated_data.get("passport_country")
        profile.passport_issue_date = validated_data.get("passport_issue_date")
        profile.passport_expiry_date = validated_data.get("passport_expiry_date")
        profile.save()
        return profile


class CustomerProfileLabelSerializer(serializers.ModelSerializer):
    # labels = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    mother_fullname = serializers.SerializerMethodField()
    father_fullname = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    any_previous_marriage = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city_of_birth = serializers.SerializerMethodField()
    first_language = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    current_country = serializers.SerializerMethodField()
    desired_country = serializers.SerializerMethodField()
    type_of_visa = serializers.SerializerMethodField()
    marital_status = serializers.SerializerMethodField()
    passport_number = serializers.SerializerMethodField()
    passport_country = serializers.SerializerMethodField()
    passport_issue_date = serializers.SerializerMethodField()
    passport_expiry_date = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    eye_color = serializers.SerializerMethodField()
    funds_available = serializers.SerializerMethodField()

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

    def get_any_previous_marriage(self, obj):
        var = obj.previous_marriage
        if "labels" in self.context:
            return {
                "value": var,
                "type": "drop-down",
                "choices": CustomerProfile.PREV_TYPE,
                "labels": self.context["labels"]["any_previous_marriage_label"],
            }

    def get_email(self, obj):
        var = obj.email
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["email_label"],
            }

    def get_city_of_birth(self, obj):
        var = obj.city_of_birth
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["city_of_birth_label"],
            }

    def get_first_language(self, obj):
        var = obj.first_language
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["first_language_label"],
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

    def get_marital_status(self, obj):
        var = obj.marital_status
        if "labels" in self.context:
            return {
                "value": var,
                "type": "drop-down",
                "choices": MARITAL_TYPE,
                "display_spouse": 2,
                "labels": self.context["labels"]["marital_status_label"],
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
    def get_type_of_visa(self, obj):
        var = obj.type_of_visa
        if "labels" in self.context:
            return {
                "value": var,
                "type": "drop-down",
                "choices": VISA_TYPE,
                "labels": self.context["labels"]["type_of_visa_label"],
            }

    def get_passport_number(self, obj):
        var = obj.passport_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["passport_number_label"],
            }

    def get_passport_country(self, obj):
        var=None; name=None;
        if obj.passport_country is not None:
            var = obj.passport_country.id
            name = obj.passport_country.name
        if "labels" in self.context:
            return {
                "value": var,
                "name": name,
                "type": "drop-down",
                "labels": self.context["labels"]["passport_country_label"],
            }

    def get_passport_issue_date(self, obj):
        var = obj.passport_issue_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["passport_issue_date_label"],
            }

    def get_passport_expiry_date(self, obj):
        var = obj.passport_expiry_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["passport_expiry_date_label"],
            }

    def get_height(self, obj):
        var = obj.height
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["height_label"],
            }

    def get_eye_color(self, obj):
        var = obj.eye_color
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["eye_color_label"],
            }

    def get_funds_available(self, obj):
        var = obj.funds_available
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["funds_available_label"],
            }

    class Meta:
        model = CustomerProfileLabel
        fields = (
            "first_name",
            "last_name",
            # "date_of_birth",
            "age",
            "phone_number",
            "mother_fullname",
            "father_fullname",
            "current_country",
            "desired_country",
            "address",
            "type_of_visa",
            "marital_status",
            "any_previous_marriage",
            "email",
            "city_of_birth",
            "first_language",
            'passport_number',
            'passport_country',
            'passport_issue_date',
            'passport_expiry_date',
            'height',
            'eye_color',
            'funds_available',
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
            "owner",
        )


class CustomerQualificationsLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    year_of_passing = serializers.SerializerMethodField()
    # city = serializers.SerializerMethodField()
    # state = serializers.SerializerMethodField()
    # country = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_owner(self, obj):
        return {
            "value": self.context.get('owner'),
            "type": "char",
            "labels": "",
        }

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
            country, state, city = None, None, None
            if obj.country is not None and obj.city is not None and obj.state is not None:
                country, state, city = obj.country, obj.state, obj.city
            return {
                "type": "address",
                "countryLabel": self.context["labels"]["country_label"],
                "country": country.name if country else "",
                "countryId": country.id if country else "",
                "stateLabel": self.context["labels"]["state_label"],
                "state": state.state if state else "",
                "stateId": state.id if state else "",
                "cityLabel": self.context["labels"]["city_label"],
                "city": city.city_name if city else "",
                "cityId": city.id if city else "",
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
            # "country",
            # "state",
            # "city",
            "start_date",
            "end_date",
            "labels",
            "full_address",
            "owner",
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

    end_date = serializers.DateField(required=False, allow_null=True)

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
            "is_current_job",
            "owner",
        )


class WorkExperienceLabelSerializer(serializers.ModelSerializer):
    labels = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    job_type = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    job_description = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    # city = serializers.SerializerMethodField()
    # state = serializers.SerializerMethodField()
    # country = serializers.SerializerMethodField()
    weekly_working_hours = serializers.SerializerMethodField()
    is_current_job = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_owner(self, obj):
        return {
            "value": self.context.get('owner'),
            "type": "char",
            "labels": "",
        }

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
                "is_optional": True,
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["end_date_label"],
            }

    def get_is_current_job(self, obj):
        var = obj.is_current_job
        if var is None:
            var = False
        if "labels" in self.context:
            return {
                "is_optional": True,
                "value": var,
                "type": "checkbox",
                "labels": self.context["labels"]["is_current_job_label"],
            }

    def get_job_description(self, obj):
        var = obj.job_description
        if "labels" in self.context:
            return {
                "value": var,
                "type": "textarea",
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
            country, state, city = None, None, None
            if obj.country != None and obj.city != None and obj.state != None:
                country, state, city = obj.country, obj.state, obj.city
            return {
                "type": "address",
                "countryLabel": self.context["labels"]["country_label"],
                "country": country.name if country else "",
                "countryId": country.id if country else "",
                "stateLabel": self.context["labels"]["state_label"],
                "state": state.state if state else "",
                "stateId": state.id if state else "",
                "cityLabel": self.context["labels"]["city_label"],
                "city": city.city_name if city else "",
                "cityId": city.id if city else "",
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
            # "country",
            # "state",
            # "city",
            'is_current_job',
            "full_address",
            "labels",
            "owner",
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
    phone_number = serializers.IntegerField(min_value=5000000000, max_value=9999999999)


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
    verification_status = serializers.SerializerMethodField()
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

    def get_verification_status(self, obj):
        return obj.doc.verification_status

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
            "verification_status",
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
            "owner",
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
    owner = serializers.SerializerMethodField()

    def get_labels(self, obj):
        if "labels" in self.context:
            return self.context["labels"]
        return None

    def get_owner(self, obj):
        return {
            "value": self.context.get('owner'),
            "type": "char",
            "labels": "",
        }

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
                "is_optional": True,
                "value": var,
                "type": "checkbox",
                "labels": self.context["labels"]["is_blood_relationship_label"],
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
            "owner",
        )


class EducationalCreationalAssessmentSerializer(serializers.ModelSerializer):
    eca_authority_name = serializers.CharField(required=True)
    eca_authority_number = serializers.CharField(required=True)
    canadian_equivalency_summary = serializers.CharField(required=True)
    eca_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = EducationalCreationalAssessment
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
            "eca_date",
        )


class EducationalCreationalAssessmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalCreationalAssessment
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
            "eca_date",
            "owner",
        )


class EducationalCreationalAssessmentLabelSerializer(serializers.ModelSerializer):
    eca_authority_name = serializers.SerializerMethodField()
    eca_authority_number = serializers.SerializerMethodField()
    canadian_equivalency_summary = serializers.SerializerMethodField()
    eca_date = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return {
            "value": self.context.get('owner'),
            "type": "char",
            "labels": "",
        }

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

    def get_eca_date(self, obj):
        var = obj.eca_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["eca_date_label"],
            }

    class Meta:
        model = EducationalCreationalAssessmentLabel
        fields = (
            "id",
            "eca_authority_name",
            "eca_authority_number",
            "canadian_equivalency_summary",
            "eca_date",
            "owner",
        )


class LanguageScoreLabelSerializer(serializers.ModelSerializer):
    test_type = serializers.SerializerMethodField()
    test_date = serializers.SerializerMethodField()
    result_date = serializers.SerializerMethodField()
    test_version = serializers.SerializerMethodField()
    report_form_number = serializers.SerializerMethodField()
    listening_score = serializers.SerializerMethodField()
    writing_score = serializers.SerializerMethodField()
    speaking_score = serializers.SerializerMethodField()
    reading_score = serializers.SerializerMethodField()
    overall_score = serializers.SerializerMethodField()
    # mother_tongue = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_test_type(self, obj):
        var = obj.test_type
        if "labels" in self.context:
            return {
                "value": var,
                "choices": CustomerLanguageScore.TEST_TYPE,
                "type": "drop-down",
                "labels": self.context["labels"]["test_type_label"],
            }

    def get_owner(self, obj):
        return {
            "value": self.context.get('owner'),
            "type": "char",
            "labels": "",
        }

    def get_test_date(self, obj):
        var = obj.test_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["test_date_label"],
            }

    def get_result_date(self, obj):
        var = obj.result_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["result_date_label"],
            }

    def get_test_version(self, obj):
        var = obj.test_version
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["test_version_label"],
            }

    def get_report_form_number(self, obj):
        var = obj.report_form_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["report_form_number_label"],
            }

    def get_listening_score(self, obj):
        var = obj.listening_score
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["listening_score_label"],
            }

    def get_writing_score(self, obj):
        var = obj.writing_score
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["writing_score_label"],
            }

    def get_speaking_score(self, obj):
        var = obj.speaking_score
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["speaking_score_label"],
            }

    def get_reading_score(self, obj):
        var = obj.reading_score
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["reading_score_label"],
            }

    def get_overall_score(self, obj):
        var = obj.overall_score
        if "labels" in self.context:
            return {
                "value": var,
                "type": "int",
                "labels": self.context["labels"]["overall_score_label"],
            }

    class Meta:
        model = CustomerLanguageScoreLabel
        fields = ('id', 'test_type', 'result_date', 'test_version',  'report_form_number', 'listening_score', 'writing_score',
                  'speaking_score', 'reading_score', 'overall_score', 'test_date', 'owner')


class CustomerLanguageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerLanguageScore
        fields = (
            "id", 'test_type', 'test_date', 'result_date', 'test_version',  'report_form_number', 'listening_score', 'writing_score',
            'speaking_score', 'reading_score', 'overall_score', 'owner', )


class CustomerFamilyInfoUpdateSerializer(serializers.ModelSerializer):

    date_of_death = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = CustomerFamilyInformation
        fields = (
            "id", 'relationship', 'first_name', 'last_name', 'date_of_birth',  'date_of_death', 'city_of_birth', 'country_of_birth',
            'street_address', 'current_country', 'current_state', 'current_occupation', )


class CustomerSpouseProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSpouseProfile
        fields = (
            "id", 'date_of_marriage', 'number_of_children', 'first_name', 'last_name',  'mother_fullname',
            'father_fullname', 'age', 'passport_number', 'passport_country', 'passport_issue_date', 'passport_expiry_date')


class CustomerSpouseProfileLabelSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    date_of_marriage = serializers.SerializerMethodField()
    number_of_children = serializers.SerializerMethodField()
    mother_fullname = serializers.SerializerMethodField()
    father_fullname = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    passport_number = serializers.SerializerMethodField()
    passport_country = serializers.SerializerMethodField()
    passport_issue_date = serializers.SerializerMethodField()
    passport_expiry_date = serializers.SerializerMethodField()

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

    def get_date_of_marriage(self, obj):
        var = obj.date_of_marriage
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["date_of_marriage_label"],
            }

    def get_number_of_children(self, obj):
        var = obj.number_of_children
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["number_of_children_label"],
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

    def get_passport_number(self, obj):
        var = obj.passport_number
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["passport_number_label"],
            }

    def get_passport_country(self, obj):
        var = None;
        name = None;
        if obj.passport_country is not None:
            var = obj.passport_country.id
            name = obj.passport_country.name
        if "labels" in self.context:
            return {
                "value": var,
                "name": name,
                "type": "drop-down",
                "labels": self.context["labels"]["passport_country_label"],
            }

    def get_passport_issue_date(self, obj):
        var = obj.passport_issue_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["passport_issue_date_label"],
            }

    def get_passport_expiry_date(self, obj):
        var = obj.passport_expiry_date
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["passport_expiry_date_label"],
            }

    class Meta:
        model = CustomerSpouseProfileLabel
        fields = (
            "id",
            "first_name",
            "last_name",
            "number_of_children",
            "date_of_marriage",
            "age",
            "mother_fullname",
            "father_fullname",
            'passport_number',
            'passport_country',
            'passport_issue_date',
            'passport_expiry_date',
        )


class CustomerFamilyInfoLabelSerializer(serializers.ModelSerializer):
    relationship = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    date_of_death = serializers.SerializerMethodField()
    city_of_birth = serializers.SerializerMethodField()
    country_of_birth = serializers.SerializerMethodField()
    street_address = serializers.SerializerMethodField()
    current_country = serializers.SerializerMethodField()
    current_state = serializers.SerializerMethodField()
    current_occupation = serializers.SerializerMethodField()

    def get_relationship(self, obj):
        var = obj.relationship
        if "labels" in self.context:
            return {
                "value": var,
                "choices": CustomerFamilyInformation.RELATION_TYPE,
                "type": "drop-down",
                "labels": self.context["labels"]["relationship_label"],
            }

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

    def get_date_of_birth(self, obj):
        var = obj.date_of_birth
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "labels": self.context["labels"]["date_of_birth_label"],
            }

    def get_date_of_death(self, obj):
        var = obj.date_of_death
        if "labels" in self.context:
            return {
                "value": var,
                "type": "calendar",
                "is_optional": True,
                "labels": self.context["labels"]["date_of_death_label"],
            }

    def get_city_of_birth(self, obj):
        var = obj.city_of_birth
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["city_of_birth_label"],
            }

    def get_country_of_birth(self, obj):
        var = obj.country_of_birth.id
        name = obj.country_of_birth.name
        if "labels" in self.context:
            return {
                "value": var,
                "name": name,
                "type": "drop-down",
                "labels": self.context["labels"]["country_of_birth_label"],
            }

    def get_street_address(self, obj):
        var = obj.street_address
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["street_address_label"],
            }

    def get_current_country(self, obj):
        var = obj.current_country.id
        name = obj.current_country.name
        if "labels" in self.context:
            return {
                "value": var,
                "name": name,
                "type": "drop-down",
                "labels": self.context["labels"]["current_country_label"],
            }

    def get_current_state(self, obj):
        var = obj.current_state
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                # "depends": 'current_country',
                "labels": self.context["labels"]["current_state_label"],
            }

    def get_current_occupation(self, obj):
        var = obj.current_occupation
        if "labels" in self.context:
            return {
                "value": var,
                "type": "char",
                "labels": self.context["labels"]["current_occupation_label"],
            }

    class Meta:
        model = CustomerFamilyInformationLabel
        fields = ('id', 'relationship', 'first_name', 'last_name',  'date_of_birth', 'date_of_death', 'city_of_birth',
                  'country_of_birth', 'street_address', 'current_country', 'current_state', 'current_occupation', )
