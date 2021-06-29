from config.settings.production import *

ALLOWED_HOSTS = ['*']

DEBUG=False

PRODUCTION = False

PRIVATE_FILE_STORAGE = 'keel.Core.storage_backends.PrivateMediaStorage'
STATICFILES_STORAGE = 'keel.Core.storage_backends.StaticStorage'
DEFAULT_FILE_STORAGE = 'keel.Core.storage_backends.PublicMediaStorage'

STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
