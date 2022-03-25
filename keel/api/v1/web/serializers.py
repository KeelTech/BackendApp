from rest_framework import serializers
from keel.web.models import HomeLeads, WebsiteContactData



class WebsiteContactDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteContactData
        fields = ('id', 'name', 'email', 'phone', 'message')


class HomeLeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeLeads
        fields = ('id', 'name', 'email', 'phone')