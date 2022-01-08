from django.db.models import fields
from keel.questionnaire.models import (
    AnsweredQuestionsModel,
    CheckBoxModel,
    DropDownModel,
    Question,
    QuestionnaireAnalysis,
    SpouseQuestion,
)
from rest_framework import serializers


class CheckBoxSerializer(serializers.ModelSerializer):
    # checkbox_id = serializers.SerializerMethodField()

    class Meta:
        model = CheckBoxModel
        fields = (
            "id",
            "checkbox_text",
            "with_spouse_score",
            "without_spouse_score",
        )

    # def get_checkbox_id(self, obj):
    #     return obj.id


class DropDownSerializer(serializers.ModelSerializer):
    # dropdown_id = serializers.SerializerMethodField()

    class Meta:
        model = DropDownModel
        fields = (
            "id",
            "dropdown_text",
            "with_spouse_score",
            "without_spouse_score",
        )

    # def get_dropdown_id(self, obj):
    #     return obj.id


class SpouseQuestionSerializer(serializers.ModelSerializer):
    text_choice = serializers.SerializerMethodField()
    answer_type_value = serializers.CharField(source="get_answer_type_display")
    dropdown_choice = serializers.SerializerMethodField()
    checkbox_choice = serializers.SerializerMethodField()

    class Meta:
        model = SpouseQuestion
        fields = (
            "id",
            "question_text",
            "answer_type",
            "answer_type_value",
            "key",
            "text_choice",
            "dropdown_choice",
            "checkbox_choice",
            "is_active",
        )

    def get_text_choice(self, obj):
        return ""

    def get_dropdown_choice(self, obj):
        queryset = obj.spouse_question_dropdown.all()
        serializer = DropDownSerializer(queryset, many=True).data
        return serializer

    def get_checkbox_choice(self, obj):
        queryset = obj.spouse_question_checkbox.all()
        serializer = CheckBoxSerializer(queryset, many=True).data
        return serializer


class QuestionSerializer(serializers.ModelSerializer):
    text_choice = serializers.SerializerMethodField()
    answer_type_value = serializers.CharField(source="get_answer_type_display")
    dropdown_choice = serializers.SerializerMethodField()
    checkbox_choice = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "answer_type",
            "answer_type_value",
            "key",
            "text_choice",
            "dropdown_choice",
            "checkbox_choice",
            "is_active",
        )

    def get_text_choice(self, obj):
        return ""

    def get_dropdown_choice(self, obj):
        queryset = obj.question_dropdown.all()
        serializer = DropDownSerializer(queryset, many=True).data
        return serializer

    def get_checkbox_choice(self, obj):
        queryset = obj.question_checkbox.all()
        serializer = CheckBoxSerializer(queryset, many=True).data
        return serializer


class AnsweredQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsweredQuestionsModel
        fields = ("id", "email", "question", "answer")


class QuestionnaireAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireAnalysis
        fields = ("id", "question", "uuid", "created_at")
