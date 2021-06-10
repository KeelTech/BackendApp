from django.urls import path

from .views import CustomerLeadView

urlpatterns = [
    path('create', CustomerLeadView.as_view({'post': 'create'}), name='leads-create'),
]
