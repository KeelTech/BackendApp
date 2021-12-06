import re

from django.core.mail import send_mail
from django.conf import settings
from .err_log import log_error
from .exceptions import InvalidDataType
from .helpers import get_connection, save_triggered_email

class SMSNotification:

    def __init__(self, number, text):

        self.number = number
        self.text = text

    def validate_sms(self):
        err = ''
        try:
            int(self.number)
        except:
            err = "Invalid number passed"
            return err

        if not self.text:
            err = "Invalid SMS Text"
        return err

    def send_sms(self):
        err = ''
        err = self.validate_sms()
        if err:
            log_error("ERROR", "SMSNotification: validate_sms", "", err = err)
            return err 
        try:
            path = settings.SMS_BACKEND
            resp = get_connection(path).send_sms(self.number, self.text)
            log_error("INFO", "SMSNotification: send_sms", "", resp = str(resp))
        except Exception as e:
            log_error("CRITICAL", "SMSNotification: send_sms", "", err = str(e))
            err = str("Failed to send email")
        return err


class EmailNotification:

    TEXT = 'text'
    HTML = 'html'

    def __init__(self, subject, content, to_list, content_type = HTML, cc = [], bcc= []):

        self.subject = subject
        self.content = content
        self.to_list = to_list
        self.cc = cc
        self.bcc = bcc
        self.content_type = content_type

    def validate_email(self, email_id):

        email_regex = r"(^[a-zA-Z0-9_.+-/']+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, email_id):
            return False
        return True

    def validation_email_obj(self):
        err = ''
        if not self.subject:
            err = "Email Subject is empty" 
            return err

        if len(self.to_list) == 0:
            err = "Recipients list is empty" 
            return err

        valid = all([self.validate_email(i) for i in self.to_list ])
        if not valid:
            err = "Invalid Email Id"
            log_error("ERROR","EmailNotification:validation_email_obj","", err = err, to_list = self.to_list)
            return err
        return err

    def send_email(self):
        err = ''
        err = self.validation_email_obj()
        if err:
            log_error("ERROR", "EmailNotification:validation_email_obj", "", err = err)
            return err 
        try:

            # if self.content_type == self.HTML:
            #     send_mail(self.subject, self.content, settings.SENDER_EMAIL, self.to_list, html_message = self.content)
            # else:
            # send_mail(self.subject, self.content, settings.SENDER_EMAIL, self.to_list)
            path = settings.EMAIL_BACKEND
            save_triggered_email(self.to_list, self.subject)
            get_connection(path).send_email(self.subject, self.content, settings.SENDER_EMAIL, self.to_list, self.content_type)
        except Exception as e:
            log_error("CRITICAL", "EmailNotification:send_mail", "", err = str(e))
            err = str("Failed to send email")
        return err



class SendNotification:

    EMAIL = 0
    SMS = 1

    NOTIFICATION_TYPES_DICT = {
                                EMAIL: 'email',
                                SMS: 'sms',
                            } 

    def __init__(self, notif_type, email_obj= None, sms_obj= None):

        self.notif_type_list = notif_type
        self.email_obj = email_obj
        self.sms_obj = sms_obj

    def validate_data(self):
        err = ''
        for notif_type in self.notif_type_list:
            if not self.NOTIFICATION_TYPES_DICT[notif_type]:
                err = 'Invalid Notification Type %s'.format(notif_type)
                return err

            if notif_type == self.EMAIL and not self.email_obj:
                err = 'Email Notification object is missing for Email notification type'
                return err

            if notif_type == self.SMS and not self.sms_obj:
                err = 'SMS Notification object is missing for SMS notification type'
                return err

        return err

    def trigger_notification(self):
        """
        This function is to send notifications as per defined notification_types & objects
        Recommended to put inside a Try Exception block

        Raises: InvalidDataType Exception

        Returns: A dict
            <Key> : Int - Notification Type
            <Value>: dict - About the responses for each notification triggers

        """
        response_dict = {}
        err = self.validate_data()
        if err:
            log_error('ERROR', "SendNotification:validate_data", "", err = err)
            raise InvalidDataType(err)
        for notif_type in self.notif_type_list:

            if notif_type == self.EMAIL:
                mail_err = self.email_obj.send_email()
                if mail_err:
                    response_dict[self.EMAIL] = {"status": "Failed", "err":mail_err}
                else:
                    response_dict[self.EMAIL] = {"status": "Success"}

            if notif_type == self.SMS:
                mail_err = self.sms_obj.send_sms()
                if mail_err:
                    response_dict[self.EMAIL] = {"status": "Failed", "err":mail_err}
                else:
                    response_dict[self.EMAIL] = {"status": "Success"}

        return response_dict







