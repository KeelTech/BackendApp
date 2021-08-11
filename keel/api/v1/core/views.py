from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from keel.Core.models import Country, City
from .serializers import CitySerializer, CountrySerializer


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


class CityView(GenericViewSet):
    serializer_class = CitySerializer

    def get_city(self, request, **kwargs):
        response = {
            "status" : 1,
            "message" : ""
        }
        country_id = self.kwargs['id']
        country = Country.objects.get(id=country_id)
        city = City.objects.filter(country=country)
        serializer = self.serializer_class(city, many=True).data
        response["message"] = serializer
        return Response(response)