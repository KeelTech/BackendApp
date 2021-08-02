from keel.authentication.models import CustomToken
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import datetime, calendar
from django.conf import settings
from rest_framework import authentication, exceptions
import jwt
import base64


User = get_user_model()


class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'email': username, 'user_type': 1}
        else:
            kwargs = {'phone_number': username, 'user_type': 1}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX']

    def authenticate(self, request):

        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        user_key = settings.USER_SECRET_KEY
        try:
            CustomToken.objects.get(token=token)
        except CustomToken.DoesNotExist:
            msg = 'Invalid Token'
            raise exceptions.AuthenticationFailed(msg)

        try:
            payload = jwt.decode(token, user_key)
        except Exception as e:
            msg = 'Invalid authentication.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['user_id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)

    def authenticate_header(self, request):
        return self.authentication_header_prefix

    @classmethod
    def jwt_payload_handler(cls, user, exp=None):
        if not exp:
            exp = datetime.datetime.utcnow() + settings.JWT_AUTH['JWT_EXPIRATION_DELTA']
        return {
            'user_id': user.pk,
            'exp': exp,
            'orig_iat': calendar.timegm(
                datetime.datetime.utcnow().utctimetuple()
            )
        }

    @staticmethod
    def generate_token(user, request=None):
        user_key = settings.USER_SECRET_KEY    
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        payload = JWTAuthentication.jwt_payload_handler(user, exp)
        # token = jwt.encode(payload, user_key[0].key).decode('UTF-8')
        token = jwt.encode(payload, user_key, algorithm="HS256").decode('UTF-8')  # this will be changed back to line 99
        return {'token': token,
                'payload': payload}