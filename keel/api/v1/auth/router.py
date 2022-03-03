from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument, LoginViewset, GeneratePasswordReset,
                    FacebookLogin, GoogleLogin, LinkedinLogin, UserDeleteTokenView, ConfirmPasswordReset, 
                    ChangePasswordView, ProfileView, WorkExperienceView, QualificationView, ItemCount,
                    RelativeInCanadaView, EducationalCreationalAssessmentView, AgentView, NewUserFromGetRequest)

urlpatterns = [
    # authentication
    path('signup', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('customer-login', LoginViewset.as_view({'post' : 'customer_login'}), name='customer-login'),
    path('agent-login', LoginViewset.as_view({'post' : 'agent_login'}), name='agent-login'),
    path('google-login', GoogleLogin.as_view(), name='google_login'),
    path('linkedin-login', LinkedinLogin.as_view(), name='linkedin-login'),
    path('facebook-login', FacebookLogin.as_view({'post' : 'fblogin'}), name='fb_login'),
    path('logout', UserDeleteTokenView.as_view({'get' : 'remove'}), name='logout'),
    path('reset-password', GeneratePasswordReset.as_view({'post' : 'token'}), name='reset-password'),
    path('confirm-password', ConfirmPasswordReset.as_view({'post' : 'confirm_reset'}), name='confirm-password'),
    path('change-password', ChangePasswordView.as_view({'post' : 'change_password_without_email'}), name='change-password'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('otp/verify', LoginOTP.as_view({'post': 'verify'}), name='otp-verify'),
    path('new-user-from-get', NewUserFromGetRequest.as_view({'get': 'new_user'}), name='new-user-from-get'),

    # profile
    path('create-profile', ProfileView.as_view({'post' : 'create_profile'}), name='create-profile'),
    path('create-initial-profile', ProfileView.as_view({'post' : 'create_initial_profile'}), name='create-initial-profile'),
    path('create-full-profile', ProfileView.as_view({'post' : 'create_full_profile'}), name='create-full-profile'),
    path('update-full-profile', ProfileView.as_view({'post' : 'update_full_profile'}), name='update-full-profile'),
    path('get-profile', ProfileView.as_view({'get' : 'get_profile'}), name='get-profile'),
    path('get-full-profile', ProfileView.as_view({'get' : 'get_full_profile'}), name='get-full-profile'),
    path('get-agent-profile', AgentView.as_view({'get' : 'agent_profile'}), name='agent_profile'),
    path('create-qualification', QualificationView.as_view({'post' : 'qualification'}), name='create-qualification'),
    path('get-qualification', QualificationView.as_view({'get' : 'get_qualification'}), name='get-qualification'),
    path('create-work-experience', WorkExperienceView.as_view({'post':'work_exp'}), name='create-work-experience'),
    path('get-work-experience', WorkExperienceView.as_view({'get':'get_work_experience'}), name='get-work-experience'),
    path('create-relative', RelativeInCanadaView.as_view({'post':'relative_in_canada'}), name='create-relative'),
    path('get-relative', RelativeInCanadaView.as_view({'get':'get_relative_in_canada'}), name='get-relative'),
    path('create-educational-assessment', EducationalCreationalAssessmentView.as_view({'post':'educational_creational_assessment'}), name='create-educational-assessment'),
    path('get-educational-assessment', EducationalCreationalAssessmentView.as_view({'get':'get_educational_creational_assessment'}), name='get-educational-assessment'),

    # document
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
    path('get-user-doc',UploadDocument.as_view({'get':'fetch'}), name='get-docs'),
    path('delete-doc/<int:id>',UploadDocument.as_view({'delete':'deleteUserDoc'}), name='delete-docs'),
    path('item-count', ItemCount.as_view({'get':'getItemCount'}), name='get-item-count'),
]
