from django.urls import path
from .views import CountryView, CityView


urlpatterns = [
    path('countries', CountryView.as_view({'get' : 'get_country'}), name="countries"),
    path('cities/<int:id>', CityView.as_view({'get' : 'get_city'}), name="cities"),
]