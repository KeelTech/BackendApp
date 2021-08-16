from django.db import models
from rest_framework import serializers
from keel.Core.models import Country, City, State


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'name')


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ('id', 'country', 'state')

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'state', 'city_name')