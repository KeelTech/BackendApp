
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
        response = {
            "status": 0,
            "error": "",
            "data": {}
        }
        customer = request.user
        data = request.data
        payment_manager = PaymentManager()
        try:
            payment_details = payment_manager.generate_payment_details(
                StructNewPaymentDetailArgs(customer_id=customer.pk, customer_currency="usd",
                                           initiator_id=customer.pk, payment_client_type=PAYMENT_CLIENT_TYPE,
                                           case_id=data.get("case_id")),
                data["order_items"]
            )
            response["status"] = 1
            response["data"] = payment_details
        except ValueError as err:
            response["error"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            response["error"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
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
