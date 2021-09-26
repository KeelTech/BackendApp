from django.urls import path

from .views import PaymentTransactionViewSet, OrderViewSet

urlpatterns = [
    path("transactions/pending", PaymentTransactionViewSet.as_view({"get": "pending_transactions"})),
    path("order/create", OrderViewSet.as_view({"post": "create"})),
]
