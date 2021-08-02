from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument, LoginViewset, GeneratePasswordReset,
                    FacebookLogin, GoogleLogin, LinkedinLogin, UserDeleteTokenView, 
                    ConfirmPasswordReset, ChangePasswordView, ProfileView, CreateQualificationView, CreateWorkExperienceView,
                    ItemCount)

urlpatterns = [
    path('signup', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('login', LoginViewset.as_view({'post' : 'login'}), name='login'),
    path('get-profile', ProfileView.as_view({'get' : 'get_profile'}), name='get-profile'),
    path('create-profile', ProfileView.as_view({'post' : 'create_profile'}), name='create_profile'),
    path('logout', UserDeleteTokenView.as_view({'get' : 'remove'}), name='logout'),
    path('google-login', GoogleLogin.as_view(), name='google_login'),
    path('linkedin-login', LinkedinLogin.as_view(), name='linkedin-login'),
    path('facebook-login', FacebookLogin.as_view({'post' : 'fblogin'}), name='fb_login'),
    path('create-qualification', CreateQualificationView.as_view({'post' : 'qualification'}), name='create-qualification'),
    path('create-work-experience', CreateWorkExperienceView.as_view({'post' : 'work_exp'}), name='create-work-experience'),
    path('reset-password', GeneratePasswordReset.as_view({'post' : 'token'}), name='reset-password'),
    path('confirm-password', ConfirmPasswordReset.as_view({'post' : 'confirm_reset'}), name='confirm-password'),
    path('change-password', ChangePasswordView.as_view({'post' : 'change_password_without_email'}), name='change-password'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
    path('get-user-doc',UploadDocument.as_view({'get':'fetch'}), name='get-docs'),
    path('delete-doc/<int:id>',UploadDocument.as_view({'delete':'deleteUserDoc'}), name='delete-docs'),
    path('item-count', ItemCount.as_view({'get':'getItemCount'}), name='get-item-count'),
]
