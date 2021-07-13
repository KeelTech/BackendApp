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

    doc = models.ForeignKey(Documents,on_delete=models.deletion.DO_NOTHING, related_name='to_document')
    user = models.ForeignKey(User, on_delete=models.deletion.DO_NOTHING, related_name='to_user')

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


