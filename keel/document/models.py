import os

from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.Core.helpers import generate_unique_id
from keel.Core.storage_backends import PrivateMediaStorage
from .exceptions import DocumentInvalid
from .utils import validate_files, upload_files_to
from datetime import date, datetime, timedelta


# Create your models here.

class DocumentsManager(models.Manager):

    def add_attachments(self, files, user_id):

        err_msg = ''
        err_msg = validate_files(files)
        if err_msg:
            raise DocumentInvalid(err_msg)

        docs = []
        for file in files.values():
            docs.append(self.model(avatar =file, 
                                    doc_type = Documents.GENERIC, 
                                    owner_id = user_id,
                                    original_name= file.name,
                                    doc_pk= generate_unique_id(self.model.DOCUMENT_PREFIX)))

        self.bulk_create(docs, batch_size=1000)
        return docs

class Documents(TimeStampedModel,SoftDeleteModel):

    GENERIC = 0
    PASSPORT = 1
    DOC_TYPE_CHOICES = ((GENERIC, 'Generic'),
                        (PASSPORT,'Passport'))

    DOCUMENT_PREFIX = "doc_"

    doc_pk = models.CharField(max_length=255, primary_key=True)
    # doc_url = models.URLField(max_length=1000, null=True, blank=True)
    avatar = models.FileField(("Documents"), upload_to=upload_files_to,
                              blank=True, storage=PrivateMediaStorage())
    doc_type = models.SmallIntegerField(default=GENERIC, choices=DOC_TYPE_CHOICES)
    owner_id = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)

    objects = DocumentsManager()



