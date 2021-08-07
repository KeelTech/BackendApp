from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduleUrl
from .apis import CalendlyApis

from keel.call_schedule.models import CallSchedule

import logging
logger = logging.getLogger('app-logger')


class BusinessLogic(object):

    @staticmethod
    def update_call_schedule(call_schedule_id, event_invitee_details):
        call_schedule_status = event_invitee_details["status"] if not event_invitee_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "start_time": event_invitee_details["start_time_utc"],
            "end_time": event_invitee_details["end_time_utc"],
            "status": call_schedule_status
        }
        calendly_call_schedule_details = {
            "scheduled_event_invitee_url": event_invitee_details["event_invitee_url"],
            "cancel_call_url": event_invitee_details["cancel_url"],
            "reschedule_call_url": event_invitee_details["reschedule_url"],
            "communication_means": event_invitee_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.get(id=call_schedule_id).update(**call_schedule_details)
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule__id=call_schedule_id). \
                update(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    @staticmethod
    def create_call_schedule(visitor_user_obj, host_user_obj, event_invitee_details):
        call_schedule_status = event_invitee_details["status"] if not event_invitee_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "visitor_user": visitor_user_obj,
            "host_user": host_user_obj,
            "start_time": event_invitee_details["start_time_utc"],
            "end_time": event_invitee_details["end_time_utc"],
            "status": call_schedule_status
        }
        calendly_call_schedule_details = {
            "scheduled_event_invitee_url": event_invitee_details["event_invitee_url"],
            "cancel_call_url": event_invitee_details["cancel_url"],
            "reschedule_call_url": event_invitee_details["reschedule_url"],
            "communication_means": event_invitee_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.create(**call_schedule_details)
            calendly_call_schedule_details["call_schedule"] = call_schedule_obj
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.create(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    @staticmethod
    def get_event_invitee_details(scheduled_event_invitee_url):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        event_invitee_details = CalendlyApis.get_scheduled_event_invitee_details(scheduled_event_invitee_url)
        if not event_invitee_details["status"]:
            response["error"] = "Error in getting Scheduled Event Invitee details"
            return response
        event_details = CalendlyApis.get_scheduled_event_details(
            event_invitee_details["data"]["event_resource_url"])

        if not event_details["status"]:
            response["error"] = "Error in getting Scheduled Event details"
            return response
        response["data"] = event_invitee_details.update(event_details)
        return response

    def get_agent_schedule_url(self, invitee_obj, rcic_user_obj):

        scheduling_url = ""
        if not rcic_user_obj:
            return scheduling_url
        try:
            invitee_sch_url_detail = CalendlyInviteeScheduleUrl.objects.get(invitee_user=invitee_obj, host_user=rcic_user_obj)
            return invitee_sch_url_detail.schedule_url
        except ObjectDoesNotExist as err:
            pass

        try:
            calendly_user_details = CalendlyUsers.objects.get(user=rcic_user_obj)
        except ObjectDoesNotExist as err:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: error getting "
                         "calendly user details for user {} with error {}".format(rcic_user_obj.email, err))
            return scheduling_url
        # event_resource_url = CalendlyApis.get_user_event_type(calendly_user_details.user_resource_url)
        if not calendly_user_details.event_type_resource_url:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: event resource url not present for the "
                         "calendly user: {}".format(rcic_user_obj.email))
            return scheduling_url

        scheduling_url = CalendlyApis.single_use_scheduling_link(calendly_user_details.event_type_resource_url, 5,
                                                       invitee_obj.name, invitee_obj.email)
        CalendlyInviteeScheduleUrl.objects.create(invitee_user=invitee_obj, host_user=rcic_user_obj,
                                                  scheduled_url=scheduling_url)
        return scheduling_url

    def create_event_schedule(self, visitor_user_obj, host_user_obj, scheduled_event_invitee_url):
        response = {
            "status": 1,
            "data": {},
            "error": ""
        }
        event_invitee_details = BusinessLogic.get_event_invitee_details(scheduled_event_invitee_url)

        if not event_invitee_details["status"]:
            response["error"] = event_invitee_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = BusinessLogic.create_call_schedule(
            visitor_user_obj, host_user_obj, event_invitee_details["data"])
        response["data"] = {
            "schedule_id": call_schedule_obj.pk,
            "reschedule_url": calendly_call_schedule_obj.reschedule_call_url,
            "cancel_url": calendly_call_schedule_obj.cancel_call_url,
            "status": call_schedule_obj.status
        }
        return response

    def cancel_reschedule_scheduled_event(self, schedule_obj):
        response = {
            "status": 0,
            "message": "",
            "error": ""
        }
        calendly_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule=schedule_obj, is_active=True)
        event_invitee_details = BusinessLogic.get_event_invitee_details(calendly_schedule_obj.scheduled_event_invitee_url)

        if not event_invitee_details["status"]:
            response["error"] = event_invitee_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = BusinessLogic.update_call_schedule(
            schedule_obj.id, event_invitee_details["data"])
        response["status"] = 1
        response["message"] = "Cancel/Reschedule event successful"

        return response

    def get_scheduled_event_details(self, schedule_obj):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        try:
            calendly_schedule = CalendlyCallSchedule.objects.get(call_schedule=schedule_obj)
        except Exception as err:
            response["error"] = "No calendly details for the schedule"
            return response

        event_invitee_details = BusinessLogic.get_event_invitee_details(calendly_schedule.scheduled_event_invitee_url)
        if not event_invitee_details["status"]:
            response["error"] = event_invitee_details["error"]
            return response

        event_invitee_details["data"]["schedule_id"] = schedule_obj.id
        response["status"] = 1
        response["data"] = event_invitee_details["data"]
        return response


calendly_business_logic = BusinessLogic()
