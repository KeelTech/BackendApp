from django.urls import path
from django.conf.urls import include

from .stripe.router import urlpatterns as stripe_urls

urlpatterns = [
    path("stripe/", include(stripe_urls)),
]
