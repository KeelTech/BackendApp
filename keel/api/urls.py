from django.conf.urls import url, include
from django.urls import path

from .v1.auth.router import urlpatterns as auth_url


urlpatterns = [
    path('v1/user/', include(auth_url)),
   
]
