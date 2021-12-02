from django.conf import settings
from django.contrib.admin.options import ModelAdmin
from django.db import models
from keel.Core.models import SoftDeleteModel, TimeStampedModel

class Question(TimeStampedModel, SoftDeleteModel):

    TEXT=1
    CHECKBOX=2
    DROPDOWN=3

    ANSWER_TYPE_CHOICES = (
        (TEXT, 'Text'),
        (CHECKBOX, 'Checkbox'),
        (DROPDOWN, 'Dropdown'),
    )
    
    
    question_text = models.TextField(help_text="The question text.")
    answer_type = models.PositiveSmallIntegerField(choices=ANSWER_TYPE_CHOICES, help_text="The answer type.")
    is_active = models.BooleanField(default=True, help_text="Is the question active?")

    def __str__(self):
        return self.question_text


class CheckBoxModel(TimeStampedModel, SoftDeleteModel):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name='question_checkbox')
    checkbox_text = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self) -> str:
        return self.question.question_text + ' ' + self.checkbox_text


class DropDownModel(TimeStampedModel, SoftDeleteModel):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name='question_dropdown')
    dropdown_text = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self) -> str:
        return "Question: {} Related Answer: {}".format(self.question.question_text, self.dropdown_text)


class AnsweredQuestionsModel(TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='user_answered_questions')
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name='question_answered')
    answer = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.user.username + ' ' + self.question.question_text
    
    class Meta:
        verbose_name = "Answered Question"
        verbose_name_plural = "Answered Questions"
        db_table = 'keel_answered_questions'