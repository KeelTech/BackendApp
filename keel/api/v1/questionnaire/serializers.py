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
            "dependent_question",
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
            "dependent_question",
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

class DependentQuestionSerializer(serializers.ModelSerializer):
    dependent_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = "__all__"
    
    def get_dependent_answer(self, obj):
        if obj.answer_type == Question.TEXT:
            return obj.question_text
        elif obj.answer_type == Question.DROPDOWN:
            queryset = obj.question_dropdown.all()
            serializer = DropDownSerializer(queryset, many=True).data
            return serializer
        elif obj.answer_type == Question.CHECKBOX:
            queryset = obj.question_checkbox.all()
            serializer = CheckBoxSerializer(queryset, many=True).data
            return serializer
        else:
            return ""


class QuestionSerializer(serializers.ModelSerializer):
    text_choice = serializers.SerializerMethodField()
    answer_type_value = serializers.CharField(source="get_answer_type_display")
    index = serializers.IntegerField()
    dropdown_choice = serializers.SerializerMethodField()
    checkbox_choice = serializers.SerializerMethodField()
    # dependent_question = serializers.SerializerMethodField()

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
            # "dependent_question",
            "is_active",
            "index"
        )

    def get_text_choice(self, obj):
        return ""
    
    # def get_dependent_question(self, obj):
    #     answer_type = obj.answer_type
    #     if answer_type == 2:
    #         queryset = obj.dependent_question_checkbox.all()
    #     if answer_type == 3:
    #         queryset = obj.question_dropdown.all()
    #         print(queryset, "\n----------------------------------------------------------")
    #     else:
    #         return ""

    #     if len(queryset) > 0:
    #         first_item = queryset[0].dependent_question
    #     else:
    #         return ""
            
        serializer =  DependentQuestionSerializer(queryset, many=True).data
        return serializer

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
