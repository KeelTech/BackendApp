from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from keel.Core.models import BaseModel
from keel.Core.helpers import generate_unique_id
from .exceptions import DocumentInvalid
from .utils import upload_files
from datetime import date, datetime, timedelta


# Create your models here.

class DocumentsManager(models.Manager):

	def add_attachments(self, files, user_id):

		err_msg = ''
		err_msg, url_list = upload_files(files)
		if err_msg:
			raise DocumentInvalid(err_msg)

		docs = []

		for url in url_list:
			docs.append(self.model(doc_url = url, 
									doc_type = Documents.GENERIC, 
									owner_id = user_id,
									doc_pk= generate_unique_id(self.model.DOCUMENT_PREFIX)))

		self.bulk_create(docs, batch_size=1000)
		return docs

class Documents(BaseModel):

	GENERIC = 0
	PASSPORT = 1
	DOC_TYPE_CHOICES = ((GENERIC, 'Generic'),
						(PASSPORT,'Passport'))

	DOCUMENT_PREFIX = "doc_"

	doc_pk = models.CharField(max_length=255, primary_key=True)
	doc_url = models.URLField(max_length=1000, null=True, blank=True)
	doc_type = models.SmallIntegerField(default=GENERIC, choices=DOC_TYPE_CHOICES)
	owner_id = models.CharField(max_length=255)

	objects = DocumentsManager()



