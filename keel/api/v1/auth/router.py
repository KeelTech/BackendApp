from django.urls import path

from .views import (LoginOTP, UserViewset, LoginViewset)

urlpatterns = [
    path('signup/', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('login/', LoginViewset.as_view({'post' : 'login'}), name='login'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
]
