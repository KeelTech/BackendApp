import logging

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property

from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.document.models import Documents
from keel.plans.models import Service
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import logging_format
from keel.Core.models import Country, City, State
from keel.api.v1.auth.helpers import email_helper


# from safedelete import SOFT_DELETE
# from safedelete.models import SafeDeleteModel

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    
    CUSTOMER=1
    RCIC=2
    ACCOUNT_MANAGER=3
    STAFF=4

    USER_TYPE_CHOICES = (
        (CUSTOMER, 'CUSTOMER'),
        (RCIC, 'RCIC'),
        (ACCOUNT_MANAGER, 'ACCOUNT_MANAGER'),
        (STAFF, 'STAFF'),
    )
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username=None
    first_name = None
    phone_number = models.CharField(max_length=10, blank=False, null=True, default=None)
    email = models.EmailField(max_length=100, blank=False, null=True, default=None, unique=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, verbose_name="User Types", default=CUSTOMER, null=True)
    is_active = models.BooleanField(verbose_name= 'Active', default=True, help_text= 'Designates whether this user should be treated as active.')
    is_verified = models.BooleanField(verbose_name="Verified", default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    call_default_contact = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['']

    EMAIL_FIELD = 'email'
    objects = CustomUserManager()

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if self and other and self.id and other.id:
            return self.id == other.id
        return False

    def __str__(self):
        return str(self.email)

    def get_profile_name(self):
        name = None
        try:
            name = self.user_profile.get_user_name
        except ObjectDoesNotExist as err:
            err_msg = "No Profile for user - {} and type - {} while getting profile name " \
                      "with err _ {}".format(self.pk, self.user_type, err)
            logger.info(logging_format(LOGGER_LOW_SEVERITY, "User:get_profile_name",
                                       self.pk, description=err_msg))
        return name

    def get_profile_id(self):
        profile_id = None
        try:
            profile_id = self.user_profile.pk
        except ObjectDoesNotExist as err:
            err_msg = "No Profile for user - {} and type - {} while getting profile id " \
                      "with err _ {}".format(self.pk, self.user_type, err)
            logger.info(logging_format(LOGGER_LOW_SEVERITY, "User:get_profile_id",
                                       self.pk, description=err_msg))
        return profile_id
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # trigger welcome email only on new user creation
            email_helper.send_welcome_email(self.email)
            
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (("email", "phone_number"))
        db_table = "auth_user"
        ordering = ['-id']


class UserDocument(TimeStampedModel, SoftDeleteModel):

    from keel.tasks.models import Task
    
    doc = models.ForeignKey(Documents,on_delete=models.deletion.DO_NOTHING, related_name='to_document')
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='to_user')
    task = models.ForeignKey(Task, on_delete=models.deletion.DO_NOTHING, related_name='tasks_docs', null=True, blank=True)

    def __str__(self):
        return "Document belongs to {}".format(self.user.email)


class CustomToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_id", null=True)
    token = models.CharField(max_length=512, blank=False, null=True, default=None)

    class Meta:
        db_table = "custom_token"
    
    def __str__(self):
        return str(self.user)


class PasswordResetToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="password_reset_user_id", null=True)
    reset_token = models.CharField(max_length=512, blank=True, null=True, default=None, unique=True)
    expiry_date = models.DateTimeField(default=None, null=True, blank=False)

    def __str__(self) -> str:
        return "Reset token {} belongs to {}".format(self.reset_token, self.user)

    class Meta:
        db_table = "password_reset_token"


class UserService(TimeStampedModel, SoftDeleteModel):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_user_services")
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING, related_name = "services_user_services")
    quantity = models.IntegerField(null=True, blank=True)
    limit_exists = models.BooleanField(verbose_name= 'Active', default=True)
    expiry_time = models.DateTimeField(null=True, blank= True)

    def __str__(self):
        return self.user.email

class CustomerProfile(TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=512, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=512, blank=True, null=True, default=None)
    mother_fullname = models.CharField(max_length=512, blank=True, null=True, default=None)
    father_fullname = models.CharField(max_length=512, blank=True, null=True, default=None)
    age = models.CharField(max_length=512, blank=True, null=True, default=None)
    address = models.CharField(max_length=512, blank=True, null=True, default=None)
    date_of_birth = models.DateField(default=None, null=True,blank=False)
    current_country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="current_country_profile", 
                                        default=None, blank=True, null=True)
    desired_country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="desired_country_profile", 
                                        default=None, blank=True, null=True)
    
    def __str__(self):
        return str(self.user)

    @cached_property
    def get_user_name(self):
        full_name = ""
        if self.first_name:
            full_name = self.first_name

        if self.last_name:
            full_name = full_name + " " + self.last_name

        return full_name


class AgentProfile(TimeStampedModel, SoftDeleteModel):
    agent = models.OneToOneField(User, related_name="agent_user_profile", on_delete=models.DO_NOTHING)
    full_name = models.CharField(max_length=512, default=None, null=True, blank=True)
    license = models.CharField(max_length=512, default=None, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="country_agent_profile", default=None, blank=True, null=True)

    def __str__(self) -> str:
        return self.full_name
    
    class Meta:
        db_table = "agent_profile"


class AccountManagerProfile(AgentProfile):

    class Meta:
        db_table = "account_manager_profile"


class CustomerProfileLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(default="user", max_length=512)
    first_name_label = models.CharField(max_length=512)
    last_name_label = models.CharField(max_length=512)
    mother_fullname_label = models.CharField(max_length=512)
    father_fullname_label = models.CharField(max_length=512)
    age_label = models.CharField(max_length=512)
    address_label = models.CharField(max_length=512)
    date_of_birth_label = models.CharField(max_length=512)
    phone_number_label = models.CharField(max_length=512, blank=True, null=True, default=None)
    current_country_label = models.CharField(max_length=512, blank=True, null=True, default=None)
    desired_country_label = models.CharField(max_length=512, blank=True, null=True, default=None)


class CustomerQualifications(TimeStampedModel, SoftDeleteModel):

    # BACHELORS = 1
    # MASTERS = 2

    # DEGREE_TYPE = (
    #     (BACHELORS, 'BACHELORS'),
    #     (MASTERS, 'MASTERS'),
    # )

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_qualification")
    institute = models.CharField(max_length=512, default=None, blank=True, null=True)
    degree = models.CharField(max_length=512, default=None,  blank=True, null=True)
    grade = models.CharField(max_length=512, blank=True, null=True, default=None)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name="city_customer_qualification", 
                                max_length=512, blank=True, null=True, default=None)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name="state_customer_qualification", 
                                            blank=True, null=True, default=None)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="country_customer_qualifcation",
                                        max_length=512, blank=True, null=True, default=None)
    year_of_passing = models.CharField(max_length=512, blank=True, null=True, default=None)
    start_date = models.DateField(max_length=512, blank=True, null=True, default=None)
    end_date = models.DateField(max_length=512, blank=True, null=True, default=None)

    def __str__(self):
        return str(self.user)


class QualificationLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(default="user", max_length=512)
    institute_label = models.CharField(max_length=512)
    degree_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    grade_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    year_of_passing_label = models.CharField(max_length=512)
    city_label = models.CharField(max_length=512)
    state_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    country_label = models.CharField(max_length=512)
    start_date_label = models.CharField(max_length=512)
    end_date_label = models.CharField(max_length=512)


class CustomerWorkExperience(TimeStampedModel, SoftDeleteModel):
    
    PART_TIME = 1
    FULL_TIME = 2

    JOB_TYPE = (
        (PART_TIME, 'PART_TIME'),
        (FULL_TIME, 'FULL_TIME'),
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_workexp")
    start_date = models.DateField(max_length=512, default=None, blank=True, null=True)
    end_date = models.DateField(max_length=512, default=None, blank=True, null=True)
    job_type = models.CharField(max_length=512, default=None, blank=True, null=True)
    designation = models.CharField(max_length=512, default=None, blank=True, null=True)
    job_description = models.CharField(max_length=512, default=None, blank=True, null=True)
    company_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name="city_customer_experience", 
                                max_length=512, blank=True, null=True, default=None)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name="state_customer_experience", 
                                            blank=True, null=True, default=None)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name="country_customer_experience",
                                        max_length=512, blank=True, null=True, default=None)
    weekly_working_hours = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class WorkExperienceLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=255, default="user")
    job_type_label = models.CharField(max_length=255)
    designation_label = models.CharField(max_length=255)
    job_description_label = models.CharField(max_length=255)
    company_name_label = models.CharField(max_length=255)
    city_label = models.CharField(max_length=255)
    state_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    country_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    weekly_working_hours_label = models.CharField(max_length=255)
    start_date_label = models.CharField(max_length=255)
    end_date_label = models.CharField(max_length=255)


class RelativeInCanada(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="relative_in_canada")
    full_name = models.CharField(max_length=512, default=None, null=True, blank=True)
    relationship = models.CharField(max_length=512, default=None, null=True, blank=True)
    immigration_status = models.CharField(max_length=512, default=None, null=True, blank=True)
    address = models.CharField(max_length=512, default=None, null=True, blank=True)
    contact_number = models.CharField(max_length=512, default=None, null=True, blank=True)
    email_address = models.CharField(max_length=512, default=None, null=True, blank=True)
    is_blood_relationship = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

class RelativeInCanadaLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=215, default="user")
    full_name_label = models.CharField(max_length=215)
    relationship_label = models.CharField(max_length=215)
    immigration_status_label = models.CharField(max_length=215)
    address_label = models.CharField(max_length=215)
    contact_number_label = models.CharField(max_length=215)
    email_address_label = models.CharField(max_length=215)
    is_blood_relationship_label = models.CharField(max_length=215, default=None, null=True)


class EducationalCreationalAssessment(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="educational_creational")
    eca_authority_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    eca_authority_number = models.CharField(max_length=512, default=None, blank=True, null=True)
    canadian_equivalency_summary = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.user)
        
class EducationalCreationalAssessmentLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=215, default="user")
    eca_authority_name_label = models.CharField(max_length=215)
    eca_authority_number_label = models.CharField(max_length=215)
    canadian_equivalency_summary_label = models.CharField(max_length=215)


class SMSOtpModel(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="sms_otp", null=True, blank=True, default=None)
    phone_number = models.BigIntegerField(default=None, blank=True, null=True)
    otp = models.CharField(max_length=512, default=None, blank=True, null=True)
    otp_expiry = models.DateTimeField(default=None, blank=True, null=True)
    otp_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)