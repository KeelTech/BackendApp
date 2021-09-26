
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from keel.payment.implementation.pay_manager import PaymentManager
from keel.payment.models import Order

PAYMENT_CLIENT_TYPE = Order.PAYMENT_CLIENT_STRIPE


class WebHookViewSet(GenericViewSet):

    def process_event(self, request, **kwargs):
        sig_header = request.headers.get('stripe-signature')
        try:
            payment_manager = PaymentManager()
            payment_manager.payment_webhook_event_handler(PAYMENT_CLIENT_TYPE, request.body, sig_header)
        except Exception as err:
            return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

        return Response({"success": True}, status.HTTP_200_OK)
