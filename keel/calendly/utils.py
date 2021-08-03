
from django.core.exceptions import ObjectDoesNotExist
from keel.authentication.models import User

from .models import CalendlyUsers
from .apis import CalendlyApis

import logging
logger = logging.getLogger('app-logger')


class BusinessLogic(object):

    def get_agent_schedule_url(self, invitee_name, invitee_email, rcic_user_email: str) -> str:
        scheduling_url = ""
        if not rcic_user_email:
            return scheduling_url
        try:
            calendly_user_details = CalendlyUsers.objects.get(user__email=rcic_user_email)
        except ObjectDoesNotExist as err:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: error getting "
                         "calendly user details for user {} with error {}".format(rcic_user_email, err))
            return scheduling_url
        # event_resource_url = CalendlyApis.get_user_event_type(calendly_user_details.user_resource_url)
        if not calendly_user_details.event_type_resource_url:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: event resource url not present for the "
                         "calendly user: {}".format(rcic_user_email))
            return scheduling_url

        return CalendlyApis.single_use_scheduling_link(calendly_user_details.event_type_resource_url,
                                                       invitee_name, invitee_email)


calendly_business_logic = BusinessLogic()
