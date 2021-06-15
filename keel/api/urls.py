from django.conf.urls import url, include
from django.urls import path

from rest_framework_simplejwt import views as jwt_views

from .v1.auth.router import urlpatterns as auth_url
from .v1.leads.router import urlpatterns as leads_url
from .v1.eligibility_calculator.router import urlpatterns as eligibility_url


urlpatterns = [

    #jwt tokens
    path('v1/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('v1/user/', include(auth_url)),
    path('v1/leads/', include(leads_url)),
    path('v1/eligibility/', include(eligibility_url)),
]