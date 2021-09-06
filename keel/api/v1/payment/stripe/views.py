
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from keel.authentication.backends import JWTAuthentication
from keel.authentication.models import User
from keel.payment.implementation.pay_manager import PaymentManager, StructNewPaymentDetailArgs
from keel.payment.models import CasePlanPaymentProfile
from keel.stripe.utils import STRIPE_PAYMENT_OBJECT, STRIPE_EVENT_MANAGER

PAYMENT_CLIENT_TYPE = CasePlanPaymentProfile.PAYMENT_CLIENT_STRIPE


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
        try:
            STRIPE_EVENT_MANAGER.process_event(request.data)
        except Exception as err:
            return Response(status.HTTP_400_BAD_REQUEST)
