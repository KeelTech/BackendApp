from config.settings.production import *

ALLOWED_HOSTS = ['*']

DEBUG=False

PRODUCTION = False

PRIVATE_FILE_STORAGE = 'keel.Core.storage_backends.PrivateMediaStorage'
STATICFILES_STORAGE = 'keel.Core.storage_backends.StaticStorage'
DEFAULT_FILE_STORAGE = 'keel.Core.storage_backends.PublicMediaStorage'

STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)

## SEND GRID EMAIL SETTINGS
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY') 
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDGRID_USER_NAME = os.getenv('SENDGRID_USER_NAME')
EMAIL_HOST_USER = SENDGRID_USER_NAME
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'keel.Core.notification_backend.SMTPEmailBackend'
SMS_BACKEND = 'keel.Core.notification_backend.SMSBackend'


FAST_2_SMS_URL = os.getenv("FAST_2_SMS_URL")
FAST_2_SMS_KEY = os.getenv("FAST_2_SMS_KEY")
