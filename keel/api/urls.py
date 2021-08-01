from django.conf.urls import url, include
from django.urls import path

from .v1.router import urlpatterns as v1_url

urlpatterns = [
    path('v1/', include(v1_url)),
]