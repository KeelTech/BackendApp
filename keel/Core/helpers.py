import os
import uuid
from random import randint
from urllib.parse import urlparse

import boto3
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_module
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error

from .models import TriggeredEmails

# from config.settings.production import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 
#                                     AWS_S3_REGION, AWS_STORAGE_BUCKET_NAME)

def get_s3_confing():
    if not settings.get('AWS_ACCESS_KEY_ID'):
        return False
    s3_config =  boto3.resource('s3',
                             region_name=settings.AWS_S3_REGION,
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                            )                           
    return s3_config

def generate_unique_id(prefix):
    return prefix + str(uuid.uuid4().hex)


def upload_file_to_s3(file):
    project_path = os.path.abspath(os.path.join(os.path.dirname( __name__ ), '.'))
    file_path = project_path + "/UserDocuments/"

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    parsed = urlparse(file.name)
    root, ext = os.path.splitext(parsed.path)
    if not ext:
        try:
            ext = "." + file.name.split(".")[-1]
        except Exception as e:
            ext = ""

    file_name = generate_unique_id('doc_') + ext
    file_full_path = file_path + file_name
    f = open(file_full_path, 'wb')
    f.write(file.read())
    f.close()
    s3_config = get_s3_confing()
    if s3_config:
        response = s3_config.meta.client.upload_file(
                                    file_full_path, 
                                    S3_BUCKET_NAME, 
                                    "/UserDocuments/"+file_name
                                    )
    ## return with URLs
    return


def get_connection(path):
    try:
        mod_name, class_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured('Error importing  backend %s: "%s"' % (mod_name, e))

    try:
        class_ref = getattr(mod, class_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, class_name))

    return class_ref()

def generate_random_int(n):

    start_range = 10**(n-1)
    end_range = 10**n - 1
    return randint(start_range,end_range)


def save_triggered_email(email, subject):
    triggered_email = TriggeredEmails(email=email, subject=subject)
    try:
        triggered_email.save()
    except Exception as e:
        log_error(LOGGER_LOW_SEVERITY, "save_triggered_email", "",
                description="error in saving triggered email",)
    return triggered_email
