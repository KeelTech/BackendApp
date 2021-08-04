from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import CalendlyUsers, CalendlyCallSchedule
from .apis import CalendlyApis

from keel.call_schedule.models import CallSchedule

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

    def create_event_schedule(self, visitor_user_obj, host_user_obj, scheduled_event_invitee_url):
        event_invitee_details = CalendlyApis.get_scheduled_event_invitee_details(scheduled_event_invitee_url)
        if not event_invitee_details["status"]:
            # Handle exception case
            pass
        event_details = CalendlyApis.get_scheduled_event_details(event_invitee_details["event_resource_url"])

        if not event_details["status"]:
            # Handle exception case
            pass
        response = {
            "status": 1,
            "data": {},
            "error": ""
        }

        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.create(
                visitor_user=visitor_user_obj, host_user=host_user_obj, start_time=event_details["start_time_utc"],
                end_time=event_details["end_time_utc"])
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.create(
                call_schedule=call_schedule_obj, scheduled_event_invitee_url=scheduled_event_invitee_url,
                cancel_call_url=event_details["cancel_url"], reschedule_call_url=event_details["reschedule_url"],
                communication_means=event_details["location"]
            )
            response["data"] = {
                "schedule_id": call_schedule_obj.pk,
                "reschedule_url": calendly_call_schedule_obj.reschedule_call_url,
                "cancel_url": calendly_call_schedule_obj.cancle_call_url
            }
        return response

    @staticmethod
    def reschedule_scheduled_event(schedule_obj, new_scheduled_event_invitee_url):
        response = {
            "status": 1,
            "message": "Scheduled event rescheduled",
            "error": ""
        }
        new_event_invitee_details = CalendlyApis.get_scheduled_event_invitee_details(new_scheduled_event_invitee_url)
        if not new_event_invitee_details["status"]:
            # Handle exception case
            pass
        new_event_details = CalendlyApis.get_scheduled_event_details(new_event_invitee_details["event_resource_url"])

        if not new_event_details["status"]:
            # Handle exception case
            pass

        with transaction.atomic():
            pass

        return response

    @staticmethod
    def cancel_scheduled_event(schedule_obj):
        response = {
            "status": 1,
            "message": "Schedule Canceled",
            "error": ""
        }

        with transaction.atomic():
            schedule_obj.status = CallSchedule.CANCELED
            schedule_obj.save()
            try:
                calendly_call_schedule = schedule_obj.calendly_schedule_details.get(is_active=True)
                calendly_call_schedule.status = CallSchedule.CANCELED
                calendly_call_schedule.save()
            except ObjectDoesNotExist as err:
                # Log error
                response["status"] = 0
                response["error"] = "Calendly Schedule for the schedule does not exists"

        return response


calendly_business_logic = BusinessLogic()
