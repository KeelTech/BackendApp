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

class IeltsData(TimeStampedModel):
    READING = 1
    WRITING = 2
    SPEAKING = 3
    LISTENING = 4
    ALLMODULES = 5
    MODULE_CHOICES = (
        (READING, 'Reading'),
        (WRITING, 'Writing'),
        (SPEAKING, 'Speaking'),
        (LISTENING, 'Listening'),
        (ALLMODULES, 'All modules')
    )
    ACADEMIC = 1
    GENERAL = 2
    EXAM_TYPE_CHOICES = (
        (ACADEMIC, 'Academic'),
        (GENERAL, 'General')
    )
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    DAY_CHOICES = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday')
    )
    title = models.CharField(max_length=100, default=None)
    day = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_type = models.PositiveSmallIntegerField(choices=EXAM_TYPE_CHOICES)
    module = models.PositiveSmallIntegerField(choices=MODULE_CHOICES)
    ielts_img = models.FileField(
        ("Ielts Image"), upload_to="ielts", blank=True)

class JobPostingData(TimeStampedModel):
    DESIGN = 1
    DEVELOPMENT = 2
    SALES = 3
    MARKETING = 4
    UI_UX = 5
    CATEGORY_CHOICES = (
        (DESIGN, 'DESIGN'),
        (DEVELOPMENT, 'DEVELOPMENT'),
        (SALES, 'SALES'),
        (MARKETING, 'MARKETING'),
        (UI_UX, 'UI/UX'),
    )
    GURUGRAM = 1
    REMOTE = 2
    GURUGRAM_REMOTE = 3
    LOCATION_CHOICES = (
        (GURUGRAM, 'Gurugram'),
        (REMOTE, 'Remote'),
        (GURUGRAM_REMOTE, 'Gurugram/Remote'),)
    category = models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100, default=None)
    location = models.PositiveSmallIntegerField(choices=LOCATION_CHOICES)
    experience = models.CharField(max_length=20, default=None)
    skills = models.CharField(max_length=100, default=None)
    description = models.TextField(max_length=200, default=None)
