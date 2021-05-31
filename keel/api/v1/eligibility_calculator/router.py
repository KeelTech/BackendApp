from django.urls import path

from .views import (EligibilityResultsView)

urlpatterns = [
    path('eligibility-result/', EligibilityResultsView.as_view(), name='eligibility-result'),
]
