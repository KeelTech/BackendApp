from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.conf import settings
from keel.Core.models import TimeStampedModel, SoftDeleteModel


class Question(TimeStampedModel, SoftDeleteModel):
    question = models.TextField()

    def __str__(self):
        return str(self.pk)

class Option(TimeStampedModel, SoftDeleteModel):

    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, default=None, blank=True, null=True, related_name='options')
    option = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.pk)

class AnsweredQuestionnaires(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, default=None)
    question = models.ForeignKey(Question, models.DO_NOTHING, default=None)
    answer = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __str__(self) -> str:
        return super().__str__()