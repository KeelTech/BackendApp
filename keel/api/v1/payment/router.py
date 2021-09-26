from django.urls import path
from django.conf.urls import include

from keel.api.v1.stripe.router import urlpatterns as stripe_urls
from .views import PaymentTransactionViewSet, OrderViewSet

urlpatterns = [
    path("stripe/", include(stripe_urls)),
    path("user/transactions/pending", PaymentTransactionViewSet.as_view({"get": "pending_transactions"})),
    path("order/create", OrderViewSet.as_view({"post": "create"})),
]
