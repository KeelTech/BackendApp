from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# from safedelete import SOFT_DELETE
# from safedelete.models import SafeDeleteModel

import requests
import json
import uuid
from rest_framework import status
import logging

from keel.document.models import Documents
from keel.Core.models import TimeStampedModel,SoftDeleteModel
from keel.plans.models import Service

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

    USER_TYPE_CHOICES = (
        (CUSTOMER, 'CUSTOMER'),
        (RCIC, 'RCIC'),
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


    class Meta:
        unique_together = (("email", "phone_number"))
        db_table = "auth_user"

class UserDocument(TimeStampedModel, SoftDeleteModel):

    from keel.tasks.models import Task
    
    doc = models.ForeignKey(Documents,on_delete=models.deletion.DO_NOTHING, related_name='to_document')
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='to_user')
    task = models.ForeignKey(Task, on_delete=models.deletion.DO_NOTHING, related_name='tasks_docs', null=True, blank=True)

class CustomToken(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_id", null=True)
    token = models.CharField(max_length=512, blank=False, null=True, default=None)

    class Meta:
        db_table = "custom_token"

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


class CustomerProfile(TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(User, related_name="user_profile", on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=512, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=512, blank=True, null=True, default=None)
    mother_fullname = models.CharField(max_length=512, blank=True, null=True, default=None)
    father_fullname = models.CharField(max_length=512, blank=True, null=True, default=None)
    age = models.CharField(max_length=512, blank=True, null=True, default=None)
    address = models.CharField(max_length=512, blank=True, null=True, default=None)
    date_of_birth = models.DateField(default=None, null=True,blank=False)
    current_country = models.CharField(max_length=512, default=None, blank=True, null=True)
    desired_country = models.CharField(max_length=512, default=None, blank=True, null=True)


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


class CustomerQualifications(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_qualification")
    institute = models.CharField(max_length=512, default=None, blank=True, null=True)
    grade = models.CharField(max_length=512, blank=True, null=True, default=None)
    year_of_passing = models.CharField(max_length=512, blank=True, null=True, default=None)
    city = models.CharField(max_length=512, blank=True, null=True, default=None)
    country = models.CharField(max_length=512, blank=True, null=True, default=None)
    start_date = models.DateField(max_length=512, blank=True, null=True, default=None)
    end_date = models.DateField(max_length=512, blank=True, null=True, default=None)


class QualificationLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(default="user", max_length=512)
    institute_label = models.CharField(max_length=512)
    grade_label = models.CharField(max_length=255, default=None, null=True, blank=True)
    year_of_passing_label = models.CharField(max_length=512)
    city_label = models.CharField(max_length=512)
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
    job_type = models.CharField(max_length=512, default=FULL_TIME, blank=True, null=True)
    designation = models.CharField(max_length=512, default=None, blank=True, null=True)
    job_description = models.CharField(max_length=512, default=None, blank=True, null=True)
    company_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    city = models.CharField(max_length=512, default=None, blank=True, null=True)
    weekly_working_hours = models.CharField(max_length=512, default=None, blank=True, null=True)


class WorkExperienceLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=255, default="user")
    job_type_label = models.CharField(max_length=255)
    designation_label = models.CharField(max_length=255)
    job_description_label = models.CharField(max_length=255)
    company_name_label = models.CharField(max_length=255)
    city_label = models.CharField(max_length=255)
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


class RelativeInCanadaLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=215, default="user")
    full_name_label = models.CharField(max_length=215)
    relationship_label = models.CharField(max_length=215)
    immigrations_status_label = models.CharField(max_length=215)
    address_label = models.CharField(max_length=215)
    contact_number_label = models.CharField(max_length=215)
    email_address_label = models.CharField(max_length=215)


class EducationalCreationalAssessment(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="educational_creational")
    eca_authority_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    eca_authority_number = models.CharField(max_length=512, default=None, blank=True, null=True)
    canadian_equivalency_summary = models.CharField(max_length=512, default=None, blank=True, null=True)


class EducationalCreationalAssessmentLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(max_length=215, default="user")
    eca_authority_name_label = models.CharField(max_length=215)
    eca_authority_number_label = models.CharField(max_length=215)
    canadian_equivalency_summary_label = models.CharField(max_length=215)