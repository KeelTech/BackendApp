from django.urls import include, path
from . import views

urlpatterns = [
    #path('auth/', views.obtain_auth_token),
    path('doctor/otp/generate',views.generate_otp_doctor),
    path('doctor/login',views.login_doctor),
    path('user/otp/generate',views.generate_otp_user),
    path('user/login',views.login_user),
    path('user/register',views.register_user),
    path('logout',views.logout)
]