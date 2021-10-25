from django.contrib.admin.options import ModelAdmin
from django.db import models
from django.conf import settings
from keel.Core.models import TimeStampedModel, SoftDeleteModel


class Question(TimeStampedModel, SoftDeleteModel):
    question = models.TextField()

    def __str__(self):
        return str(self.pk)

class Answer(TimeStampedModel, SoftDeleteModel):

    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    

    ANSWER_TYPE_CHOICES = (

    )
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, default=None, blank=True, null=True)
    answer = models.CharField(max_length=512, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.pk)

class CustomerAnswers(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, default=None)
    question = models.ForeignKey(Question, models.DO_NOTHING, default=None)
    answer = models.ForeignKey(Answer, models.DO_NOTHING, default=None)

    def __str__(self) -> str:
        return super().__str__()