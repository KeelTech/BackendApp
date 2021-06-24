from django.conf.urls import url, include
from django.urls import path

from .v1.auth.router import urlpatterns as auth_url
from .v1.leads.router import urlpatterns as leads_url
from .v1.eligibility_calculator.router import urlpatterns as eligibility_url
from .v1.document.router import urlpatterns as documents_url

urlpatterns = [

    path('v1/user/', include(auth_url)),
    path('v1/leads/', include(leads_url)),
    path('v1/eligibility/', include(eligibility_url)),
    path('v1/doc/', include(documents_url)),
]