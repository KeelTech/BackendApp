import re
from rest_framework import serializers
from keel.plans.models import Plan, PlatformComponents


class PlanSerializers(serializers.ModelSerializer):
    check_list = serializers.SerializerMethodField()
    plan_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Plan
        fields = ('id', 'title', 'description', 'price', 'discount', 'plan_type', 'currency', 'country_iso',
                    'sgst', 'cgst', 'check_list', 'is_active')
    
    def get_check_list(self, obj):
        check_list = obj.check_list
        enum_list = list()
        keys = ['text', 'isChecked']
        for item in check_list:
            enum_list.append(dict(zip(keys, item.split('|'))))
        return enum_list
    
    def get_plan_type(self, obj):
        word = obj.title
        m = re.match(r"premium", word.lower())
        if m:
            return "Paid"
        else:
            return "Free"


class PlatformComponentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlatformComponents
        exclude = ("created_at", "updated_at", "deleted_at", )