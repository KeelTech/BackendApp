from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import CustomToken

def generate_auth_login_token(user):
    try:
        token_to_save = JWTAuthentication.generate_token(user)
        obj, created = CustomToken.objects.get_or_create(user=user, token=token_to_save["token"])
    except Exception as e:
        return e
    return obj