from django.urls import path
from .views import FilterUserCases, FilterUserCasesDetails, CaseView

urlpatterns = [
    path('create-cases', CaseView.as_view(), name="create-case"),
    path('list-cases', FilterUserCases.as_view(), name='list-cases'),
    path('list-cases-details/<int:pk>', FilterUserCasesDetails.as_view({'get':'get_case'}), name='list-cases-details'),
]
