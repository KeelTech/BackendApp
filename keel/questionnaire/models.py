from django.conf import settings
from django.contrib.admin.options import ModelAdmin
from django.db import models
from keel.Core.models import SoftDeleteModel, TimeStampedModel


class Question(TimeStampedModel, SoftDeleteModel):

    TEXT = 1
    CHECKBOX = 2
    DROPDOWN = 3

    ANSWER_TYPE_CHOICES = (
        (TEXT, "Text"),
        (CHECKBOX, "Checkbox"),
        (DROPDOWN, "Dropdown"),
    )

    key = models.CharField(
        max_length=255, unique=True, default=None, null=True, blank=True
    )
    question_text = models.TextField(help_text="The question text.")
    answer_type = models.PositiveSmallIntegerField(
        choices=ANSWER_TYPE_CHOICES, help_text="The answer type."
    )
    is_active = models.BooleanField(default=True, help_text="Is the question active?")
    index = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.question_text


class SpouseQuestion(TimeStampedModel, SoftDeleteModel):

    TEXT = 1
    CHECKBOX = 2
    DROPDOWN = 3

    ANSWER_TYPE_CHOICES = (
        (TEXT, "Text"),
        (CHECKBOX, "Checkbox"),
        (DROPDOWN, "Dropdown"),
    )

    key = models.CharField(
        max_length=255, unique=True, default=None, null=True, blank=True
    )
    question_text = models.TextField(help_text="The question text.")
    answer_type = models.PositiveSmallIntegerField(
        choices=ANSWER_TYPE_CHOICES, help_text="The answer type."
    )
    is_active = models.BooleanField(default=True, help_text="Is the question active?")

    def __str__(self):
        return self.question_text


class CheckBoxModel(TimeStampedModel, SoftDeleteModel):
    question = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="question_checkbox"
    )
    dependent_question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name="dependent_question_checkbox",
        null=True,
        blank=True,
    )
    spouse_question = models.ForeignKey(
        SpouseQuestion,
        on_delete=models.DO_NOTHING,
        related_name="spouse_question_checkbox",
        default=None,
        blank=True,
        null=True,
    )
    checkbox_text = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )
    with_spouse_score = models.BigIntegerField(default=0, blank=True, null=True)
    without_spouse_score = models.BigIntegerField(default=0, blank=True, null=True)

    def __str__(self) -> str:
        return self.question.question_text + " " + self.checkbox_text


class DropDownModel(TimeStampedModel, SoftDeleteModel):
    question = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="question_dropdown"
    )
    dependent_question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name="dependent_question_dropdown",
        null=True,
        blank=True,
    )
    spouse_question = models.ForeignKey(
        SpouseQuestion,
        on_delete=models.DO_NOTHING,
        related_name="spouse_question_dropdown",
        default=None,
        blank=True,
        null=True,
    )
    dropdown_text = models.CharField(
        max_length=255, default=None, blank=True, null=True
    )
    with_spouse_score = models.BigIntegerField(default=0, blank=True, null=True)
    without_spouse_score = models.BigIntegerField(default=0, blank=True, null=True)

    def __str__(self) -> str:
        return "Question: {} Related Answer: {}".format(
            self.question.question_text, self.dropdown_text
        )


class AnsweredQuestionsModel(TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(max_length=255, default=None, blank=True, null=True)
    question = models.ForeignKey(
        Question,
        on_delete=models.DO_NOTHING,
        related_name="question_answered",
        default=None,
        blank=True,
        null=True,
    )
    answer = models.TextField(default=None, blank=True, null=True)

    def __str__(self):
        return self.question.question_text

    class Meta:
        verbose_name = "Answered Question"
        verbose_name_plural = "Answered Questions"
        db_table = "keel_answered_questions"


class QuestionnaireAnalysis(TimeStampedModel, SoftDeleteModel):
    question = models.ForeignKey(
        Question, on_delete=models.DO_NOTHING, related_name="question_analysis"
    )
    uuid = models.CharField(max_length=255, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)
