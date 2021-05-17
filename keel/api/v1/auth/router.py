from django.urls import path

from .views import (LoginOTP, UserViewset)

urlpatterns = [
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
]
