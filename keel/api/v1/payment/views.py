from keel.authentication.backends import JWTAuthentication
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY
from keel.Core.err_log import logging_format
from keel.payment.implementation.pay_manager import (
    PaymentManager, StructNewPaymentDetailArgs)
from keel.payment.models import Order
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .razor_payment import RazorPay
from .serializers import UserOrderDetailsSerializer

PAYMENT_CLIENT_TYPE = Order.PAYMENT_CLIENT_STRIPE
import logging

logger = logging.getLogger("app-logger")


class PaymentTransactionViewSet(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def pending_transactions(self, request, **kwargs):
        response = {"status": 1, "error": "", "message": {}}
        payment_manager = PaymentManager()
        transaction_details = payment_manager.get_pending_transaction(
            customer_id=request.user.pk
        )
        response["message"] = transaction_details
        return Response(response, status.HTTP_200_OK)


class OrderViewSet(GenericViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        response = {"status": 0, "error": "", "data": {}}
        customer = request.user
        data = request.data
        payment_manager = PaymentManager()
        try:
            payment_details = payment_manager.generate_payment_details(
                StructNewPaymentDetailArgs(
                    customer_id=customer.pk,
                    customer_currency="usd",
                    initiator_id=customer.pk,
                    payment_client_type=PAYMENT_CLIENT_TYPE,
                    case_id=data.get("case_id"),
                ),
                data["order_items"],
            )
            response["status"] = 1
            response["data"] = payment_details
        except ValueError as err:
            logger.error(
                logging_format(LOGGER_CRITICAL_SEVERITY, "OrderViewSet:create"),
                "",
                description=str(err),
            )
            response["error"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as err:
            logger.error(
                logging_format(LOGGER_CRITICAL_SEVERITY, "OrderViewSet:create"),
                "",
                description=str(err),
            )
            response["error"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response)


class UserOrderDetailsView(GenericViewSet):
    serializer_class = UserOrderDetailsSerializer

    def create(self, request):
        response = {"status": 1, "message": "Data added", "data": {}}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        amount = request.data.get("amount", 0)
        currency = request.data.get("currency", "INR")

        # save user details
        try:
            serializer.save()
        except Exception as err:
            logger.error(
                logging_format(LOGGER_CRITICAL_SEVERITY, "UserOrderDetailsView:create"),
                "",
                description=str(err),
            )
            response["status"] = 0
            response["message"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # initiate order process
        order_init = RazorPay(amount, currency, user)
        generate_order_id = order_init.create_order()

        # add details to response
        response["data"] = serializer.data
        response["data"]["order_details"] = generate_order_id
        return Response(response, status.HTTP_201_CREATED)
