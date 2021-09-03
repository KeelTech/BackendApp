from os import stat
from typing import List
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
        params = request.query_params.get('type')
        if not params:
            countries = Country.objects.all().order_by("name")
            serializer = self.serializer_class(countries, many=True)
            response["message"] = serializer.data
            return Response(response)
        if params != "desired":
            countries = Country.objects.all().order_by("name")
            serializer = self.serializer_class(countries, many=True)
            response["message"] = serializer.data
            return Response(response)
        countries = Country.objects.filter(name="Canada")
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


@csrf_exempt
def get_states(request):
    country = request.POST.get('country')
    country = Country.objects.filter(id=country).first()
    states = State.objects.filter(country=country)
    states = [{"id":int(i.id), "state":i.state} for i in states]
    return JsonResponse(data=states, safe=False)


@csrf_exempt
def get_city(request):
    state = request.POST.get('state')
    state = State.objects.filter(id=state).first()
    cities = City.objects.filter(state=state)
    cities = [{"id":i.id, "city":i.city_name} for i in cities]
    return JsonResponse(data=cities, safe=False)

