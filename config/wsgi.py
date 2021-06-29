"""
WSGI config for test project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys
# from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

from django.core.wsgi import get_wsgi_application

# if not os.environ.get('DJANGO_SETTINGS_MODULE'):
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_wsgi_application()
