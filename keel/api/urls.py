from django.conf.urls import url, include
from django.urls import path

# from .v1.auth.router import urlpatterns as auth_url

from .views import CustomerLeadView


urlpatterns = [
    # path('v1/user/', include(auth_url)),
    path('leads/', CustomerLeadView.as_view(), name="leads")
]
