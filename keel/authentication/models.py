from django.conf import settings
from django.db import models, transaction
from datetime import date, datetime, timedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# from safedelete import SOFT_DELETE
# from safedelete.models import SafeDeleteModel

import requests
import json
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    # EMAIL_FIELD = 'email'
    # objects = CustomUserManager()
    username = None
    first_name = None
    phone_number = models.CharField(max_length=10, blank=False, null=True, default=None)
    email = models.EmailField(max_length=100, blank=False, null=True, default=None, unique=True)
    # user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(verbose_name= 'Active', default=True, help_text= 'Designates whether this user should be treated as active.')
    is_staff = models.BooleanField(default=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if self and other and self.id and other.id:
            return self.id == other.id
        return False

    def __str__(self):
        return str(self.phone_number)


    class Meta:
        unique_together = (("email", "phone_number"))
        db_table = "auth_user"


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    def mark_delete(self):
        self.deleted_at = datetime.now()
        self.save()

    class Meta:
        abstract = True
