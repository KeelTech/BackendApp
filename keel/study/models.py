from django.contrib.auth import get_user_model
from django.db import models
from keel.Core.models import SoftDeleteModel, TimeStampedModel

User = get_user_model()


class StudentProfile(TimeStampedModel, SoftDeleteModel):
    first_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    nationality = models.CharField(max_length=50, default=None, blank=True, null=True)
    date_of_birth = models.DateField(default=None, null=True, blank=False)


class StudentEducation(TimeStampedModel, SoftDeleteModel):
    student_profile = models.ForeignKey(
        StudentProfile, on_delete=models.DO_NOTHING, default=None, blank=True, null=True
    )
    start_year = models.DateField(blank=True, null=True, default=None)
    end_year = models.DateField(blank=True, null=True, default=None)
    name_of_institue = models.CharField(
        max_length=100, default=None, blank=True, null=True
    )
    course_name = models.CharField(max_length=50, default=None, blank=True, null=True)
    score = models.CharField(max_length=50, default=None, blank=True, null=True)


class StudentProfileLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(default="user", max_length=10)
    first_name_label = models.CharField(max_length=10)
    last_name_label = models.CharField(max_length=10)
    nationality_label = models.CharField(max_length=10)
    date_of_birth_label = models.CharField(max_length=15)


class StudentQualificationLabel(TimeStampedModel, SoftDeleteModel):
    user_label = models.CharField(default="user", max_length=512)
    start_year_label = models.CharField(max_length=512)
    end_year_label = models.CharField(max_length=512)
    name_of_institute_label = models.CharField(max_length=512)
    course_name_label = models.CharField(
        max_length=255, default=None, null=True, blank=True
    )
    score_label = models.CharField(max_length=255, default=None, null=True, blank=True)
