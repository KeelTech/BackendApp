from django.core.mail import BadHeaderError, send_mail
from django.template.loader import get_template, render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from keel.Core.notifications import EmailNotification


def send_email(user, site, current_time):
    status = 0
    subject = "Password Reset from GetKeel"
    email_template_name = "password_reset_email.txt"
    c = {
        "email": user,
        'domain': site.domain,
        'site_name': 'Getkeel',
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token': current_time,
        'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)
    try:
        send_mail(subject, email, 'admin@getkeel.com', [user], fail_silently=False)
    except BadHeaderError:
        return status
    status = 1
    return status    


def base_send_email(subject, html_content, to_email):
    emails = EmailNotification(subject, html_content, [to_email])
    emails.send_email()


def send_welcome_email(email):
    context = {
        'name' : email
    }
    subject = 'Welcome'
    html_content = get_template('welcome_email.html').render(context)
    base_send_email(subject, html_content, email)


def send_create_task_email(context, to_email):
    subject = 'Task Created'
    html_content = get_template('task_created.html').render(context)
    base_send_email(subject, html_content, to_email)


def send_update_task_email(context, to_email):
    subject = 'Task Updated'
    html_content = get_template('task_updated.html').render(context)
    base_send_email(subject, html_content, to_email)


def send_delete_task_email(context, to_email):
    subject = 'Task Deleted'
    html_content = get_template('task_deleted.html').render(context)
    base_send_email(subject, html_content, to_email)


def send_crs_score(context, to_email):
    subject = 'CRS Score'
    html_content = get_template('crs_score.html').render(context)
    base_send_email(subject, html_content, to_email)


def order_created_email(context, to_email):
    subject = 'Order Created'
    html_content = get_template('order_created.html').render(context)
    base_send_email(subject, html_content, to_email)