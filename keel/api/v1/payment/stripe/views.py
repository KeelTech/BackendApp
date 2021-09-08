
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from keel.authentication.backends import JWTAuthentication
from keel.payment.implementation.pay_manager import PaymentManager, StructNewPaymentDetailArgs
from keel.payment.models import Order
from keel.stripe.utils import STRIPE_EVENT_MANAGER

PAYMENT_CLIENT_TYPE = Order.PAYMENT_CLIENT_STRIPE


class OrderViewSet(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        user = request.user
        data = request.data
        payment_manager = PaymentManager()
        response = payment_manager.generate_payment_details(
            StructNewPaymentDetailArgs(customer_id=user.pk, customer_currency="usd", initiator_id=user.pk,
                                       payment_client_type=PAYMENT_CLIENT_TYPE),
            data
        )
        return Response(response)


class WebHookViewSet(GenericViewSet):

    def process_event(self, request, **kwargs):
        sig_header = request.headers.get('stripe-signature')
        try:
            payment_manager = PaymentManager()
            payment_manager.payment_webhook_event_handler(PAYMENT_CLIENT_TYPE, request.body, sig_header)
        except Exception as err:
            return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

        return Response({"success": True}, status.HTTP_200_OK)
