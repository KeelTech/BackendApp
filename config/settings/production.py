from config.settings.base import *
import logging

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['getkeel.com','admin.keel.com']

DATABASES['default']['ATOMIC_REQUESTS'] = True  # noqa F405
# DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)
DEBUG = False


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
#SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
#SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
#SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
#CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
# CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 360000
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = True
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = 'DENY'

INSTALLED_APPS += ('gunicorn',)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, env('LOG_DIR')))
LOG_FILE = env('LOG_FILE')

# create directory for log file
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['console', ],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format':  '%(levelname)s %(asctime)s %(process)d %(thread)d %(name)s.%(module)s:%(lineno)d %(message)s',
        },
    },
    'handlers': {
        'file' : {
            'level' : 'INFO',
            'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : os.path.join(LOG_DIR, LOG_FILE),
            'backupCount': 10,
            'maxBytes': 15 * 1024 * 1024,  # 15 MB
            'formatter' : 'simple'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', ],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'app-logger': { 
            'handlers': ['file', 'console'],                                                              
            'level': 'INFO',                                                                          
            'propagate': True,                                                                            
        },   
    },
}
PRODUCTION=True

LEADAPITOKEN = "HVGVGJYG00"

PRIVATE_FILE_STORAGE = 'keel.Core.storage_backends.PrivateMediaStorage'
STATICFILES_STORAGE = 'keel.Core.storage_backends.StaticStorage'
DEFAULT_FILE_STORAGE = 'keel.Core.storage_backends.PublicMediaStorage'

AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME') ## TODO Change this
AWS_S3_REGION = env('AWS_S3_REGION')

AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)



AWS_QUERYSTRING_AUTH = False
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }

AWS_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'keel.Core.storage_backends.StaticStorage'
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
## TODO check them
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'keel.Core.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'keel.Core.storage_backends.PrivateMediaStorage'


## SEND GRID EMAIL SETTINGS
SENDER_EMAIL = env('SENDER_EMAIL')
EMAIL_HOST_USER =  env('SENDGRID_USER_NAME')
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'keel.Core.notification_backend.SMTPEmailBackend'
SMS_BACKEND = 'keel.Core.notification_backend.SMSBackend'


FAST_2_SMS_URL = os.getenv("FAST_2_SMS_URL")
FAST_2_SMS_KEY = os.getenv("FAST_2_SMS_KEY")



