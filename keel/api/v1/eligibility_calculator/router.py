from django.urls import path

from .views import (EligibilityResultsView, CrsCalculatorView)

urlpatterns = [
    path('eligibility-result/', EligibilityResultsView.as_view({'post': 'submit'}), name='eligibility-result-submit'),
    path('crs-calculate/', CrsCalculatorView.as_view(), name="crs-calculate"),
]
