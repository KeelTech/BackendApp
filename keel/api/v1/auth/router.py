from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument)

urlpatterns = [
    path('signup/', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
]
