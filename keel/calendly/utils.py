from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import CalendlyUsers, CalendlyCallSchedule, CalendlyInviteeScheduledUrl
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
            "invitee_url": event_invitee_details["event_invitee_url"],
            "cancel_url": event_invitee_details["cancel_url"],
            "reschedule_url": event_invitee_details["reschedule_url"],
            "communication_means": event_invitee_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.get(id=call_schedule_id).update(**call_schedule_details)
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule__id=call_schedule_id). \
                update(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    @staticmethod
    def create_call_schedule(visitor_user_obj, host_user_obj, event_details):
        call_schedule_status = event_details["status"] if not event_details[
            "rescheduled"] else CallSchedule.RESCHEDULED
        call_schedule_details = {
            "visitor_user": visitor_user_obj,
            "host_user": host_user_obj,
            "start_time": event_details["start_time_utc"],
            "end_time": event_details["end_time_utc"],
            "status": call_schedule_status
        }
        calendly_call_schedule_details = {
            "invitee_url": event_details["invitee_url"],
            "cancel_url": event_details["cancel_url"],
            "reschedule_url": event_details["reschedule_url"],
            "communication_means": event_details["location"],
            "status": call_schedule_status
        }
        with transaction.atomic():
            call_schedule_obj = CallSchedule.objects.create(**call_schedule_details)
            calendly_call_schedule_details["call_schedule"] = call_schedule_obj
            calendly_call_schedule_obj = CalendlyCallSchedule.objects.create(**calendly_call_schedule_details)
            return call_schedule_obj, calendly_call_schedule_obj

    @staticmethod
    def get_event_details(invitee_url):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        invitee_details = CalendlyApis.get_invitee_details(invitee_url)
        if not invitee_details["status"]:
            response["error"] = "Error in getting Invitee details"
            return response
        event_details = CalendlyApis.get_event_details(
            invitee_details["data"]["event_resource_url"])

        if not event_details["status"]:
            response["error"] = "Error in getting Event details"
            return response
        event_details["data"].update(invitee_details["data"])
        response["data"] = event_details["data"]
        response["status"] = 1
        return response

    def get_agent_schedule_url(self, invitee_obj, rcic_user_obj):

        scheduling_url = ""
        if not rcic_user_obj:
            return scheduling_url
        try:
            invitee_sch_url_detail = CalendlyInviteeScheduledUrl.objects.get(invitee_user=invitee_obj, host_user=rcic_user_obj)
            return invitee_sch_url_detail.scheduled_call_url
        except ObjectDoesNotExist as err:
            pass

        try:
            calendly_user_obj = CalendlyUsers.objects.get(user=rcic_user_obj)
        except ObjectDoesNotExist as err:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: error getting "
                         "calendly user details for user {} with error {}".format(rcic_user_obj.email, err))
            return scheduling_url
        # event_resource_url = CalendlyApis.get_user_event_type(calendly_user_details.user_resource_url)
        if not calendly_user_obj.event_type_url:
            logger.error("CALENDLY-GET_AGENT_SCHEDULE_URL: event resource url not present for the "
                         "calendly user: {}".format(rcic_user_obj.email))
            return scheduling_url

        schedule_url_details = CalendlyApis.single_use_scheduling_link(
            calendly_user_obj.event_type_url, 100, invitee_obj.first_name, invitee_obj.email)

        if not schedule_url_details["status"]:
            return scheduling_url
        calendly_invitee_scheduled_obj = CalendlyInviteeScheduledUrl.objects.create(
            invitee_user=invitee_obj, host_user=rcic_user_obj, scheduled_call_url=schedule_url_details["schedule_url"])
        return calendly_invitee_scheduled_obj.scheduled_call_url

    def create_event_schedule(self, visitor_user_obj, host_user_obj, invitee_url):
        response = {
            "status": 1,
            "data": {},
            "error": ""
        }
        existing_calendly_schedule = CalendlyCallSchedule.objects.filter(
            invitee_url=invitee_url)
        if existing_calendly_schedule:
            calendly_call_schedule_obj = existing_calendly_schedule[0]
            call_schedule_obj = CallSchedule.objects.get(pk=calendly_call_schedule_obj.call_schedule.pk)
            response["data"] = {
                "schedule_id": call_schedule_obj.pk,
                "reschedule_url": calendly_call_schedule_obj.reschedule_url,
                "cancel_url": calendly_call_schedule_obj.cancel_url,
                "status": call_schedule_obj.readable_status
            }
            return response

        event_details = BusinessLogic.get_event_details(invitee_url)

        if not event_details["status"]:
            response["status"] = 0
            response["error"] = event_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = BusinessLogic.create_call_schedule(
            visitor_user_obj, host_user_obj, event_details["data"])
        response["data"] = {
            "schedule_id": call_schedule_obj.pk,
            "reschedule_url": calendly_call_schedule_obj.reschedule_url,
            "cancel_url": calendly_call_schedule_obj.cancel_call_url,
            "status": call_schedule_obj.readable_status
        }
        return response

    def cancel_reschedule_scheduled_event(self, schedule_obj):
        response = {
            "status": 0,
            "message": "",
            "error": ""
        }
        calendly_schedule_obj = CalendlyCallSchedule.objects.get(call_schedule=schedule_obj, is_active=True)
        event_details = BusinessLogic.get_event_details(calendly_schedule_obj.invitee_url)

        if not event_details["status"]:
            response["error"] = event_details["error"]
            return response

        call_schedule_obj, calendly_call_schedule_obj = BusinessLogic.update_call_schedule(
            schedule_obj.id, event_details["data"])
        response["status"] = 1
        response["message"] = "Cancel/Reschedule event successful"

        return response

    def get_scheduled_event_details(self, call_schedule_objs):
        response = {
            "status": 0,
            "data": {},
            "error": ""
        }
        calendly_call_schedules = CalendlyCallSchedule.objects.filter(call_schedule__in=call_schedule_objs)

        if not calendly_call_schedules:
            response["error"] = "No calendly details for the schedule"
            return response

        response_data = []
        for calendly_schedule in calendly_call_schedules:
            schedule_detail = {
                "error": "",
                "schedule_id": calendly_schedule.call_schedule.id
            }
            event_details = BusinessLogic.get_event_details(calendly_schedule.invitee_url)
            if not event_details["status"]:
                response["error"] = event_details["error"]
            else:
                details = event_details["data"]
                schedule_detail.update({
                    "status": CallSchedule.STATUS_MAP.get(details["status"]),
                    "start_time": details["start_time_utc"],
                    "end_time": details["end_time_utc"],
                    "cancel_url": details["cancel_url"],
                    "reschedule_url": details["reschedule_url"]
                })
            response_data.append(schedule_detail)

        response["status"] = 1
        response["data"] = response_data
        return response


calendly_business_logic = BusinessLogic()
