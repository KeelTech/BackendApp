import logging
from django.contrib.auth import get_user_model
from keel.authentication.models import CustomerProfile, AgentProfile
from keel.Core.constants import (LOGGER_LOW_SEVERITY)
from keel.Core.err_log import logging_format, log_error

logger = logging.getLogger('app-logger')

User = get_user_model()


def extract_user_details(user):

    if user.user_type == User.CUSTOMER:
        try:
            customer = CustomerProfile.objects.get(user=user)
        except CustomerProfile.DoesNotExist as err:
            log_error(LOGGER_LOW_SEVERITY, "extract_user_details", user.id, description=str(err))
            return user.email
        full_name = "{} {}".format(customer.first_name, customer.last_name)
        return full_name
    
    if user.user_type == User.RCIC:
        try:
            agent = AgentProfile.objects.get(agent=user)
        except AgentProfile.DoesNotExist as err:
            log_error(LOGGER_LOW_SEVERITY, "extract_user_details", user.id, description=str(err))
            return user.email
        return agent.full_name

