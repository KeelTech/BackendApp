from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument, LoginViewset, 
                    FacebookLogin, GoogleLogin, LinkedinLogin)

urlpatterns = [
    path('signup', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('login', LoginViewset.as_view({'post' : 'login'}), name='login'),
    path('google-login', GoogleLogin.as_view(), name='google_login'),
    path('linkedin-login', LinkedinLogin.as_view(), name='linkedin-login'),
    path('facebook-login', FacebookLogin.as_view(), name='fb_login'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
    path('get-user-doc',UploadDocument.as_view({'get':'fetch'}), name='get-docs'),
]
