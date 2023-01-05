from ckeditor.fields import RichTextField
from django.db import models
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.Core.storage_backends import PrivateStorage


class HtmlField(TimeStampedModel, SoftDeleteModel):
    body = RichTextField()

    class Meta:
        abstract = True


class Web(HtmlField):
    pass

    def __str__(self):
        return str(self.pk)


class WebsiteComponents(HtmlField):

    CONTACT_US = 1
    HOME = 2
    TESTIMONIALS = 3
    BLOGS = 4

    COMPONENT_NAME_CHOICES = (
        (CONTACT_US, "Contact Us"),
        (HOME, "Home"),
        (TESTIMONIALS, "Testimonials"),
        (BLOGS, "Blog"),
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    component_name = models.PositiveSmallIntegerField(
        choices=COMPONENT_NAME_CHOICES, default=CONTACT_US
    )
    blog_img = models.FileField(
        ("Blog Image"), upload_to="blog", blank=True)
    is_active = models.BooleanField(default=True)
    highlight = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)


class BaseContactData(TimeStampedModel):
    email = models.EmailField(default=None, blank=True, null=True)
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)

    class Meta:
        abstract = True


class WebsiteContactData(BaseContactData):
    name = models.CharField(max_length=100, default=None, blank=True, null=True)
    message = models.TextField(default=None, blank=True, null=True)


class HomeLeads(BaseContactData):
    pass
