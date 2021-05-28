from rest_framework import serializers
from rest_framework import validators
from .models import CustomerLead


class CustomerLeadSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True, 
                                    validators=[validators.UniqueValidator(queryset=CustomerLead.objects.all())])
    phone_number = serializers.IntegerField()
    lead_source = serializers.ChoiceField(choices=CustomerLead.LEAD_SOURCE)
    resolution = serializers.ChoiceField(choices=CustomerLead.RESOLUTION)
    

    class Meta:
        model = CustomerLead
        fields = ('id', 'email', 'phone_number', 'lead_source', 'resolution')