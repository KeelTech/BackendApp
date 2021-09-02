from keel.Core.models import City, State, Country

def city_instance(id):
    city = City.objects.get(id=id)
    return city

def state_instance(id):
    state = State.objects.get(id=id)
    return state

def country_instance(id):
    country = Country.objects.get(id=id)
    return country