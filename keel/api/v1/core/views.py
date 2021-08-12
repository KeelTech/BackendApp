from os import stat
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from keel.Core.models import Country, City, State
from .serializers import CitySerializer, CountrySerializer, StateSerializer


class CountryView(GenericViewSet):
    serializer_class = CountrySerializer
    
    def get_country(self, request):
        response = {
            "status" : 1,
            "message" : ""
        }
        countries = Country.objects.all().order_by("name")
        serializer = self.serializer_class(countries, many=True)
        response["message"] = serializer.data
        return Response(response)

class StateView(GenericViewSet):
    serializer_class = StateSerializer

    def get_state(self, request, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        country_id = self.kwargs['id']
        country = Country.objects.filter(id=country_id).first()
        state = State.objects.filter(country=country)
        serializer = self.serializer_class(state, many=True).data
        response["message"] = serializer
        return Response(response)


class CityView(GenericViewSet):
    serializer_class = CitySerializer

    def get_city(self, request, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        state_id = self.kwargs['id']
        state = State.objects.filter(id=state_id).first()
        city = City.objects.filter(state=state)
        serializer = self.serializer_class(city, many=True).data
        response["message"] = serializer
        return Response(response)