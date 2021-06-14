from rest_framework import serializers
from rest_framework import validators
from keel.leads.models import CustomerLead


class CustomerLeadSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)
    # phone_number = serializers.IntegerField(null=True)
    lead_source = serializers.ChoiceField(choices=CustomerLead.LEAD_SOURCE_CHOICES)

    
    class Meta:
        model = CustomerLead
        fields = ('id', 'email', 'phone_number', 'lead_source')