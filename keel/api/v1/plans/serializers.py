from rest_framework import serializers
from keel.plans.models import Plan


class PlanSerializers(serializers.ModelSerializer):
    check_list = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ('id', 'title', 'description', 'price', 'discount', 'currency', 'country_iso',
                    'sgst', 'cgst', 'check_list', 'is_active')
    
    def get_check_list(self, obj):
        check_list = obj.check_list
        enum_list = list()
        keys = ['text', 'isChecked']
        for item in check_list:
            enum_list.append(dict(zip(keys, item.split('|'))))
        return enum_list