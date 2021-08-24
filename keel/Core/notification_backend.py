from django.core.mail.backends.console import EmailBackend as Console
from django.core.mail.backends.smtp import EmailBackend as SMTP
from django.core.mail import send_mail
from django.conf import settings

import requests

class ConsoleEmailBackend(object):
    def send_email(self, subject, message, sender, to=[], content_type = 'html'):
        if content_type == 'html':
            send_mail(subject, message, sender, to, fail_silently=False, connection=Console(), html_message = message)
        else:
            send_mail(subject, message, sender, to, fail_silently=False, connection=Console())


class SMTPEmailBackend(object):
    def send_email(self, subject, message, sender, to, content_type = 'html'):
        if content_type == 'html':
            send_mail(subject, message, sender, to, fail_silently=False, connection=SMTP(), html_message = message)
        else:
            send_mail(subject, message, sender, to, fail_silently=False, connection=SMTP())


class ConsoleSMSBackend(object):
    def send_sms(self, number, text):
        print ("SMS phone number and body : ",number, text)

class SMSBackend(object):
    def send_sms(self, number, text):
        resp = self.send_fast2_sms(number, text)
        return resp

    ## Fast2SMS SMS sending function
    def send_fast2_sms(self, number, text):

        url = settings.FAST_2_SMS_URL
        params = {
            "authorization": settings.FAST_2_SMS_KEY,
            "route": "q",
            "message": text,
            "language": "english",
            "flash": "0",
            "numbers": number,
        }
        response = requests.request("GET", url, params=params)

        return response

