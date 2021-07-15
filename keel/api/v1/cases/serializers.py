from rest_framework import serializers
from keel.cases.models import Case


class ListCasesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Case
        fields = "__all__"