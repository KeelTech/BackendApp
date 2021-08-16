from django.urls import path
from .views import CountryView, CityView, StateView


urlpatterns = [
    path('countries', CountryView.as_view({'get' : 'get_country'}), name="countries"),
    path('states/<int:id>', StateView.as_view({'get' : 'get_state'}), name="states"),
    path('cities/<int:id>', CityView.as_view({'get' : 'get_city'}), name="cities"),
]