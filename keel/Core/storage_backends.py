from config.settings import production
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = production.AWS_STATIC_LOCATION

class PublicMediaStorage(S3Boto3Storage):
    location = production.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    location = production.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False

