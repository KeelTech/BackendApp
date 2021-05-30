from django.urls import path

from .views import CustomerLeadView

urlpatterns = [
    path('', CustomerLeadView.as_view(), name='leads'),
]
