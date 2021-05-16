from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import jwt
import datetime, calendar
from django.conf import settings
from rest_framework import authentication, exceptions
from keel.authentication.models import UserSecretKey, WhiteListedLoginTokens
import base64
from packaging.version import parse

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


class MatrixAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.MATRIX_DOC_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


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
        user_key = None
        user_id, is_agent = JWTAuthentication.get_unverified_user(token)

        if user_id:
            if not is_agent and request and request.META.get("HTTP_APP_NAME") != 'd_web' and (('HTTP_APP_VERSION' not in request.META) or
                            (request.META.get("HTTP_APP_NAME") == 'docprime_consumer_app' and parse(
                                request.META.get('HTTP_APP_VERSION')) > parse('2.7.2')) or \
                            (request.META.get("HTTP_APP_NAME") == "doc_prime_partner" and
                             (parse(request.META.get('HTTP_APP_VERSION')) > parse('2.100.15') and request.META.get(
                                  'HTTP_PLATFORM') == 'android') or
                              (parse(request.META.get('HTTP_APP_VERSION')) > parse('2.200.11') and request.META.get(
                                  'HTTP_PLATFORM') == 'ios')
                             )

            ):
            #     is_whitelisted = WhiteListedLoginTokens.objects.filter(token=token, user_id=user_id).first()
            #     if is_whitelisted:
                user_key_object = UserSecretKey.objects.filter(user_id=user_id).first()
                if user_key_object:
                    user_key = user_key_object.key
                else:
                    raise exceptions.AuthenticationFailed("Invalid Login")
            else:
                user_key_object = UserSecretKey.objects.filter(user_id=user_id).first()
                if user_key_object:
                    user_key = user_key_object.key
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
        if payload.get('agent_id', None) is not None:
            request.agent = payload.get('agent_id')

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

    @classmethod
    def appointment_agent_payload_handler(cls, request, created_user, can_book=False):
        return {
            'agent_id': request.user.id,
            'user_id': created_user.pk,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'orig_iat': calendar.timegm(
                datetime.datetime.utcnow().utctimetuple()
            ),
            'refresh': False,
            'can_book': can_book
        }

    @staticmethod
    def get_unverified_user(token):
        try:
            unverified_payload = jwt.decode(token, verify=False)
        except Exception as e:
            msg = 'Invalid authentication.'
            raise exceptions.AuthenticationFailed(msg)

        return unverified_payload.get('user_id', None), unverified_payload.get('agent_id', None)

    @staticmethod
    def generate_token(user, request=None):
        user_key = UserSecretKey.objects.get_or_create(user=user)
        if request and request.META.get("HTTP_APP_NAME") != 'd_web' and (('HTTP_APP_VERSION' not in request.META) or
                        (request.META.get("HTTP_APP_NAME")== 'docprime_consumer_app' and parse(request.META.get('HTTP_APP_VERSION')) > parse('2.7.2')) or \
                         (request.META.get("HTTP_APP_NAME") == "doc_prime_partner" and
                         (parse(request.META.get('HTTP_APP_VERSION')) > parse('2.100.15') and request.META.get(
                             'HTTP_PLATFORM') == 'android') or
                          (parse(request.META.get('HTTP_APP_VERSION')) > parse('2.200.11') and request.META.get(
                              'HTTP_PLATFORM') == 'ios')
                         )
        ):
            payload = JWTAuthentication.jwt_payload_handler(user)
        else:
            exp = datetime.datetime.utcnow() + datetime.timedelta(days=365)
            payload = JWTAuthentication.jwt_payload_handler(user, exp)
        token = jwt.encode(payload, user_key[0].key)
        # whitelist = WhiteListedLoginTokens.objects.create(token=token.decode('utf-8'), user=user)
        return {'token': token,
                'payload': payload}

    @classmethod
    def provider_sms_payload_handler(cls, user, appointment):
        return {
            'user_id': user.pk,
            'expiration_time': appointment.time_slot_start + datetime.timedelta(hours=24),
            'exp': appointment.time_slot_start + datetime.timedelta(hours=24),
            'orig_iat': calendar.timegm(
                datetime.datetime.utcnow().utctimetuple()
            ),
            'refresh': False
        }


class RefreshAuthentication(JWTAuthentication):

    def authenticate(self, request):

        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        return self._authenticate_credentials(request, token)

    @staticmethod
    def get_unverified_user(token):
        unverified_payload = jwt.decode(token, verify=False)

        return unverified_payload.get('user_id', None), unverified_payload.get('agent_id', None)

    def _authenticate_credentials(self, request, token):
        user_key = None
        user_id, is_agent = self.get_unverified_user(token)
        if is_agent:
            request.agent = True
        user = User.objects.get(pk=user_id)
        return (user, token)


class WhatsappAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.WHATSAPP_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


class ChatAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.CHAT_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


class MatrixUserAuthentication(authentication.BaseAuthentication):

    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.MATRIX_USER_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


class BajajAllianzAuthentication(authentication.BaseAuthentication):

    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.BAJAJ_ALLIANZ_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


class SbiGAuthentication(authentication.BaseAuthentication):

    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.SBIG_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


class SalespointAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Token"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix

        if not auth_header:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        if (len(auth_header) == 1) or (len(auth_header) > 2):
            raise exceptions.AuthenticationFailed('UnAuthorized')

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix.lower():
            raise exceptions.AuthenticationFailed('UnAuthorized')

        token = base64.b64decode(token)

        if token.decode('utf-8') != settings.SPO_DP_AUTH_TOKEN:
            raise exceptions.AuthenticationFailed('UnAuthorized')

        return (None, None)

    def authenticate_header(self, request):
        return self.authentication_header_prefix


# class CloudLabUserAuthentication(authentication.BaseAuthentication):
#     authentication_header_prefix = "Token"
#
#     def authenticate(self, request):
#         auth_header = authentication.get_authorization_header(request).split()
#         auth_header_prefix = self.authentication_header_prefix
#
#         if not auth_header:
#             raise exceptions.AuthenticationFailed('UnAuthorized')
#
#         if (len(auth_header) == 1) or (len(auth_header) > 2):
#             raise exceptions.AuthenticationFailed('UnAuthorized')
#
#         prefix = auth_header[0].decode('utf-8')
#         token = auth_header[1].decode('utf-8')
#
#         if prefix.lower() != auth_header_prefix.lower():
#             raise exceptions.AuthenticationFailed('UnAuthorized')
#
#         token = base64.b64decode(token)
#
#         if token.decode('utf-8') != settings.CLOUD_LAB_AUTH_TOKEN:
#             raise exceptions.AuthenticationFailed('UnAuthorized')
#
#         return (None, None)
#
#     def authenticate_header(self, request):
#         return self.authentication_header_prefix

