
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from keel.authentication.backends import JWTAuthentication
from keel.payment.implementation.pay_manager import PaymentManager


class PaymentTransactionViewSet(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def pending_transactions(self, request, **kwargs):
        response = {
            "status": 1,
            "error": "",
            "message": {}
        }
        payment_manager = PaymentManager()
        transaction_details = payment_manager.get_pending_transaction(customer_id=request.user.pk)
        response["message"] = transaction_details
        return Response(response, status.HTTP_200_OK)
