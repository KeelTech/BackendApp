from django.urls import path

from .views import (LoginOTP, UserViewset, UploadDocument, LoginViewset)

urlpatterns = [
    path('signup/', UserViewset.as_view({'post' : 'signup'}), name='signup'),
    path('login/', LoginViewset.as_view({'post' : 'login'}), name='login'),
    path('otp/generate', LoginOTP.as_view({'post': 'generate'}), name='otp-generate'),
    path('upload-doc', UploadDocument.as_view({'post':'upload'}),name='doc-upload'),
    path('get-user-doc',UploadDocument.as_view({'get':'fetch'}), name='get-docs'),
]
