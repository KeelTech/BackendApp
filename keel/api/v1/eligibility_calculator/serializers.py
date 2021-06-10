from rest_framework import serializers
from keel.eligibility_calculator.models import EligibilityResults


# This is used to validate the data[json] field containing the name and email 
class DataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()

    class Meta:
        model = EligibilityResults
        fields = ('name', 'email')

    
class EligibilityResultsSeriaizer(serializers.ModelSerializer):
    data = DataSerializer()

    class Meta:
        model = EligibilityResults
        fields = ('id', 'lead_id', 'data')


class CrsCalculatorSerializer(serializers.Serializer):
    age = serializers.CharField(max_length=30)
    education = serializers.CharField(max_length=30)
    work_experience = serializers.CharField(max_length=30)
    language_test = serializers.CharField(max_length=30)