from django.template import Context, Template
from keel.Core.constants import LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error
from keel.Core.notifications import EmailNotification
from keel.web.models import EmailTemplateModel


class EmailTemplateHelper(object):
    def __init__(self, email_template_key, context, to_email):
        self.email_template_key = email_template_key
        self.context = context
        self.to_email = to_email

    def send_email(self):
        email_template = self.get_email_template()
        if email_template["success"] == False:
            return email_template
        else:
            email_template = email_template["email_template"]

        # send email
        subject = email_template.subject
        message = email_template.body
        render_content = Template(message).render(Context(self.context))

        email = EmailNotification(subject, render_content, [self.to_email])
        email.send_email()
        return {"success": True}

    def get_email_template(self):
        response = {"success": True, "email_template": ""}
        try:
            email_template = EmailTemplateModel.objects.get(key=self.email_template_key)
            response["email_template"] = email_template
        except EmailTemplateModel.DoesNotExist:
            response["success"] = False
            response["error"] = "Email template does not exist"
        return response


def send_email_template_instance(email_template_key, context={}, to_email=""):
    email_template_helper = EmailTemplateHelper(email_template_key, context, to_email)
    resp_email = email_template_helper.send_email()
    print(resp_email)
    if resp_email["success"] == False:
        log_error(
            LOGGER_LOW_SEVERITY,
            "UserViewSet:Signup:send welcome email",
            "",
            description=resp_email["error"],
        )


# def base_send_email(subject, html_content, to_email):
#     emails = EmailNotification(subject, html_content, [to_email])
#     emails.send_email()


# def send_welcome_email(email):
#     context = {"name": email}
#     subject = "Welcome"
#     html_content = get_template("welcome_email.html").render(context)
#     base_send_email(subject, html_content, email)


# def send_create_task_email(context, to_email):
#     subject = "Task Created"
#     html_content = get_template("task_created.html").render(context)
#     base_send_email(subject, html_content, to_email)


# def send_update_task_email(context, to_email):
#     subject = "Task Updated"
#     html_content = get_template("task_updated.html").render(context)
#     base_send_email(subject, html_content, to_email)


# def send_delete_task_email(context, to_email):
#     subject = "Task Deleted"
#     html_content = get_template("task_deleted.html").render(context)
#     base_send_email(subject, html_content, to_email)


# def send_crs_score(context, to_email):
#     subject = "CRS Score"
#     html_content = get_template("crs_score.html").render(context)
#     base_send_email(subject, html_content, to_email)


# def order_created_email(context, to_email):
#     subject = "Order Created"
#     html_content = get_template("order_created.html").render(context)
#     base_send_email(subject, html_content, to_email)
