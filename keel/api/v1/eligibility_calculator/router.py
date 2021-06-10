from django.urls import path

from .views import (EligibilityResultsView)

urlpatterns = [
    path('eligibility-result/', EligibilityResultsView.as_view({'post': 'submit'}), name='eligibility-result-submit'),
]
