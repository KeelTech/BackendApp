import os

from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.Core.helpers import generate_unique_id
from keel.Core.storage_backends import PrivateStorage
from keel.Core.err_log import log_error
from .exceptions import DocumentInvalid, DocumentTypeInvalid
from .utils import validate_files, upload_files_to
from datetime import date, datetime, timedelta

# Create your models here.

class DocumentsManager(models.Manager):

    def add_attachments(self, files, user_id, doc_type):

        try:
            docs = []
            for file in files.values():
                docs.append(self.model(avatar =file, 
                                        doc_type_id = doc_type, 
                                        owner_id = user_id,
                                        original_name= file.name,
                                        doc_pk= generate_unique_id(self.model.DOCUMENT_PREFIX)))

            self.bulk_create(docs)
        except Exception as e:
            log_error("ERROR", "DocumentsManager: add_attachments", str(user_id), err = str(e))
            raise Exception(e)
        return docs

class DocumentType(TimeStampedModel, SoftDeleteModel):

    DEFAULT_PK_ID = 1 # OTHERS
    doc_type_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.doc_type_name

class Documents(TimeStampedModel,SoftDeleteModel):

    DOCUMENT_PREFIX = "doc_"

    doc_pk = models.CharField(max_length=255, primary_key=True)
    # doc_url = models.URLField(max_length=1000, null=True, blank=True)
    avatar = models.FileField(("Documents"), upload_to=upload_files_to,
                              blank=True, storage=PrivateStorage)
    doc_type = models.ForeignKey(DocumentType, on_delete=models.deletion.DO_NOTHING, default = DocumentType.DEFAULT_PK_ID,
                                 related_name='doc_type_docs')
    owner_id = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)

    objects = DocumentsManager()

    def __str__(self) -> str:
        return self.doc_pk


class PublicDocuments(TimeStampedModel, SoftDeleteModel):


    avatar = models.FileField(("PublicDocuments"),blank=True)
    original_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True, default=None)


    def __str__(self) -> str:
        return self.original_name