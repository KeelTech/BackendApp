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


class ScheduleCallSerializer(serializers.Serializer):
    calendly_invitee_url = serializers.CharField()
