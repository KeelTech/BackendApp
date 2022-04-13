from django.urls import path

from .views import (OrderViewSet, PaymentTransactionViewSet,
                    UserOrderDetailsView)

urlpatterns = [
    path(
        "transactions/pending",
        PaymentTransactionViewSet.as_view({"get": "pending_transactions"}),
    ),
    path("order/create", OrderViewSet.as_view({"post": "create"})),
    path(
        "create-order-details",
        UserOrderDetailsView.as_view({"post": "create"}),
        name="create-order-details",
    ),
]
