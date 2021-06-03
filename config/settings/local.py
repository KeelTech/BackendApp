from config.settings.base import *
# from .base import env
API_ENABLED=True
DEBUG = env.bool('DJANGO_DEBUG', default=True)
SECRET_KEY = env('DJANGO_SECRET_KEY', default='!!!SET DJANGO_SECRET_KEY!!!')

ALLOWED_HOSTS = ['*']

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

INSTALLED_APPS += ('django_extensions',)
INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

INTERNAL_IPS = ['127.0.0.1']

# create directory for log file
filepath = env('LOG_FILE_PATH')
if not os.path.exists(filepath):
    os.makedirs(filepath)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
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
            'filename' : os.path.join(filepath, env('LOG_FILE')),
            
            # when I uncomment the backupCount and maxBytes, there is "ValueError: Unable to configure handler 'file'"
            # work this way
            
            'backupCount': 10,
            'maxBytes': 15 * 1024 * 1024,  # 15 MB
            'formatter' : 'simple'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',
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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'PAGE_SIZE': 10,
    'COERCE_DECIMAL_TO_STRING': True,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        
    ),
}

PRODUCTION = False

LEADAPITOKEN = ""