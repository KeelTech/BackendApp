from django.db.models import fields
from keel.questionnaire.models import (AnsweredQuestionsModel, CheckBoxModel,
                                       DropDownModel, Question, SpouseQuestion)
from rest_framework import serializers


class CheckBoxSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckBoxModel
        fields = ('id', 'checkbox_text')


class DropDownSerializer(serializers.ModelSerializer):

    class Meta:
        model = DropDownModel
        fields = ('id', 'dropdown_text')


class SpouseQuestionSerializer(serializers.ModelSerializer):
    text_choice = serializers.SerializerMethodField()
    answer_type_value = serializers.CharField(source="get_answer_type_display")
    dropdown_choice = serializers.SerializerMethodField()
    checkbox_choice = serializers.SerializerMethodField()

    class Meta:
        model = SpouseQuestion
        fields = ('id', 'question_text', 'answer_type_value', 'text_choice',
                    'dropdown_choice', 'checkbox_choice',)

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
        fields = ('id', 'question_text', 'answer_type', 'answer_type_value',
                    'text_choice', 'dropdown_choice', 'checkbox_choice', 'is_active')
    
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
        fields = ('id', 'email', 'question', 'answer')
