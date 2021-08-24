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


def send_welcome_email(user):
    print(user)
    context = {
        'name' : user.email
    }
    subject = 'Welcome'
    html_content = get_template('welcome_email.html').render(context)
    # send email
    emails = EmailNotification(subject, html_content, [user.email])
    emails.send_email()
