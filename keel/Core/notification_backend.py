from django.core.mail.backends.console import EmailBackend as Console
from django.core.mail.backends.smtp import EmailBackend as SMTP
from django.core.mail import send_mail


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
