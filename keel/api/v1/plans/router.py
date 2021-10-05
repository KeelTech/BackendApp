from django.urls import path
from .views import PlanListView, PlanDetailView, PlanComponentsView

urlpatterns = [
    path('list-plans', PlanListView.as_view({'get':'list_plans'}), name="list-plans"),
    path('plan-details/<int:id>', PlanDetailView.as_view({'get':'plan_details'}), name="plan-details"),
    path('get-plan-components', PlanComponentsView.as_view({'get':'get_plan_component'}), name="get-plan-components")
]
