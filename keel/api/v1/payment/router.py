from django.urls import path
from django.conf.urls import include

from .stripe.router import urlpatterns as stripe_urls
from .views import PaymentTransactionViewSet

urlpatterns = [
    path("stripe/", include(stripe_urls)),
    path("user/transactions/pending", PaymentTransactionViewSet.as_view({"get": "pending_transactions"}))
]
