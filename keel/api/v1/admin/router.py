from django.urls import path
from .views import userlogin_via_agent
from .views import upload


urlpatterns = [
    path('agent/user/login', userlogin_via_agent, name='agent-login'),
    path('articles/upload-image', upload, name='article-image-upload'),
]
