from django.conf import settings
from keel.authentication.models import User
from keel.cases.models import Case


def create_user_and_case(**kwargs):
    # check if user exists
    user = User.objects.filter(email=kwargs.get("email")).first()
    if user is None:
        user = User.objects.create_user(
            email=kwargs.get("email"), password=settings.DEFAULT_USER_PASS
        )

    # check if user has case
    case = Case.objects.filter(user=user).first()
    if case is None:
        case = Case.objects.create(user=user, plan=kwargs.get("plan"))

    return user, case
