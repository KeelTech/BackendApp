from rest_framework import serializers
from keel.plans.models import Plan


class PlanSerializers(serializers.ModelSerializer):

    class Meta:
        model = Plan
        fields = ('id', 'title', 'description', 'price', 'discount', 'currency', 'country_iso',
                    'sgst', 'cgst', 'is_active')