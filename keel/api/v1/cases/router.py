from django.urls import path
from .views import FilterUserCases, FilterUserCasesDetails

urlpatterns = [
    path('list-cases', FilterUserCases.as_view({'get':'list'}), name='list-cases'),
    path('list-cases-details/<int:pk>', FilterUserCasesDetails.as_view(), name='list-cases-details'),
]
