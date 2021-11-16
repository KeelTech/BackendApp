from rest_framework import serializers
from keel.questionnaire.models import Question, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('option')


class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'question', 'options')
    
    def get_options(self, obj):
        return OptionSerializer(obj.options.all(), many=True).data