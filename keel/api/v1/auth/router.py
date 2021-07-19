from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument, LoginViewset, GeneratePasswordReset,
                    FacebookLogin, GoogleLogin, LinkedinLogin, UserDeleteTokenView, 
                    ConfirmPasswordReset, ChangePasswordView)

urlpatterns = [
    path('signup', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('login', LoginViewset.as_view({'post' : 'login'}), name='login'),
    path('logout', UserDeleteTokenView.as_view({'get' : 'remove'}), name='logout'),
    path('google-login', GoogleLogin.as_view(), name='google_login'),
    path('linkedin-login', LinkedinLogin.as_view(), name='linkedin-login'),
    path('facebook-login', FacebookLogin.as_view({'post' : 'fblogin'}), name='fb_login'),
    path('reset-password', GeneratePasswordReset.as_view({'post' : 'token'}), name='reset-password'),
    path('confirm-password', ConfirmPasswordReset.as_view({'post' : 'confirm_reset'}), name='confirm-password'),
    path('change-password', ChangePasswordView.as_view({'post' : 'change_password_without_email'}), name='change-password'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
    path('get-user-doc',UploadDocument.as_view({'get':'fetch'}), name='get-docs'),
    path('delete-doc/<int:id>',UploadDocument.as_view({'delete':'deleteUserDoc'}), name='delete-docs'),
]
