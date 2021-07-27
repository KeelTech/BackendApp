from django.urls import path
from .views import PlanListView

urlpatterns = [
    path('list-plans', PlanListView.as_view(), name="list-plans")
]
