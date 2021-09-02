from django.urls import path
from .views import CountryView, CityView, StateView, get_states, get_city


urlpatterns = [
    path('countries', CountryView.as_view({'get' : 'get_country'}), name="countries"),
    path('states/<int:id>', StateView.as_view({'get' : 'get_state'}), name="states"),
    path('cities/<int:id>', CityView.as_view({'get' : 'get_city'}), name="cities"),
    path('get-states/', get_states, name="get_states"),
    path('get-cities/', get_city, name="get_city")
]