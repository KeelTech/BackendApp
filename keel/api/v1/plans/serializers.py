from rest_framework import serializers
from keel.plans.models import Plan


class PlanSerializers(serializers.ModelSerializer):

    class Meta:
        model = Plan
        fields = "__all__"