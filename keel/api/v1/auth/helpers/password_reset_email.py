from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import send_mail, BadHeaderError

def send_email(user, site, current_time):
    status = 0
    subject = "Password Reset from GetKeel"
    email_template_name = "authentication/password_reset_email.txt"
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

