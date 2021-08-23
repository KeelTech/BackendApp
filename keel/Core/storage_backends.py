from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import get_storage_class

class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    default_acl = 'public-read'

## DO NOT import this directly into storage class for FileField
class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False


## PrivateStorage to be used when uploading files with Private settings
PrivateStorageClass = get_storage_class(settings.PRIVATE_FILE_STORAGE)
PrivateStorage = PrivateStorageClass()


