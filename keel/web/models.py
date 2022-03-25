from ckeditor.fields import RichTextField
from django.db import models
from keel.Core.models import TimeStampedModel, SoftDeleteModel


class HtmlField(TimeStampedModel, SoftDeleteModel):
    body = RichTextField()

    class Meta:
        abstract = True


class Web(HtmlField):
    pass

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
