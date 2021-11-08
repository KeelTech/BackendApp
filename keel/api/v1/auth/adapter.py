import logging

import requests
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2CallbackView,
                                                          OAuth2LoginView)
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import logging_format, log_error

logger = logging.getLogger('app-logger')

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin): 
        user = sociallogin.user
        if user.id:  
            return          
        try:
            customer = User.objects.get(email=user.email)  # if user exists, connect the account to the existing account and login
            sociallogin.state['process'] = 'connect'                
            perform_login(request, customer, 'none')
        except User.DoesNotExist as err:
            log_error(LOGGER_LOW_SEVERITY, "MySocialAccountAdapter:pre_social_login", request.user.id,
                                description=str(err))
            pass
        except Exception as err:
            log_error(LOGGER_LOW_SEVERITY, "MySocialAccountAdapter:pre_social_login", request.user.id,
                                description=str(err))
            pass
    
    def get_connect_redirect_url(self, request, socialaccount):
        pass


class GoogleOAuth2AdapterIdToken(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = "https://accounts.google.com/o/oauth2/token"
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token, "alt": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login
        

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2AdapterIdToken)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2AdapterIdToken)

