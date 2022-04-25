from django.conf import settings
from django.contrib.auth import get_user_model
from keel.api.v1.auth.helpers.email_helper import order_created_email
from keel.authentication.backends import JWTAuthentication
from keel.authentication.implementation.auth_util_helper import create_user_and_case
from keel.cases.models import Case
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_LOW_SEVERITY
from keel.Core.err_log import log_error, logging_format
from keel.payment.implementation.pay_manager import (
    PaymentManager,
    StructNewPaymentDetailArgs,
)
from keel.payment.models import Order, RazorPayTransactions
from keel.plans.implementation.plan_util_helper import get_plan_instance_with_id
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .razor_payment import RazorPay, generate_transaction_id
from .serializers import RazorpayCaptureserializer, UserOrderDetailsSerializer

User = get_user_model()

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
        response = {"status": 1, "message": "", "data": {}}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # generate transaction id
        transaction_id = generate_transaction_id()

        amount = request.data.get("amount", 0)
        currency = request.data.get("currency", "INR")
        plan_id = request.data.get("plan_id", None)
        plan_instance = get_plan_instance_with_id(plan_id)
        print(plan_instance)

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
        order_init = RazorPay(amount, currency)
        generate_order_id = order_init.create_order()
        if "id" not in generate_order_id:
            response["status"] = 0
            response["message"] = generate_order_id["error"]
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # save razor pay transaction details
        try:
            razor_pay_transaction = RazorPayTransactions(
                order_id=generate_order_id["id"],
                user_order_details=serializer.instance,
                amount=amount,
                transaction_id=transaction_id,
                currency=currency,
                plan_id=plan_instance,
            )
            razor_pay_transaction.save()
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "UserOrderDetailsView: RazorPayTreansaction Model Create Error",
                "",
                description=str(err),
            )
            response["status"] = 0
            response["message"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # send email to user after order created successfully
        email = serializer.validated_data.get("email")
        first_name = serializer.validated_data.get("first_name")
        plan = plan_instance.title
        try:
            context = {
                "plan": plan,
                "first_name": first_name,
            }
            order_created_email(context, email)
        except Exception as e:
            log_error(
                LOGGER_LOW_SEVERITY,
                "UserOrderDetailsView:Send order email failed",
                "",
                description=str(e),
            )

        data = {
            "order_id": generate_order_id["id"],
            "transaction_id": transaction_id,
        }
        response["data"] = data
        return Response(response, status.HTTP_200_OK)


class CaptureRazorpayPayment(GenericViewSet):
    serializer_class = RazorpayCaptureserializer

    def verify_payment_signature(self, request):
        response = {"status": 1, "message": "Payment verified", "data": {}}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        payment_id = validated_data.get("payment_id", None)
        transaction_id = validated_data.get("transaction_id", None)
        order_id = validated_data.get("order_id", None)

        # retrieve transaction details with transaction_id and order_id
        razor_pay_transaction = (
            RazorPayTransactions.objects.select_related("user_order_details")
            .filter(transaction_id=transaction_id, order_id=order_id)
            .first()
        )
        if razor_pay_transaction is None:
            response["status"] = 0
            response["message"] = "Transaction not found"
            return Response(response, status.HTTP_404_NOT_FOUND)

        # update payment_id in razor_pay_transaction
        try:
            razor_pay_transaction.payment_id = payment_id
            razor_pay_transaction.save()
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "CaptureRazorpayPayment:verify_payment_signature",
                "",
                description=str(err),
            )
            response["status"] = 0
            response["message"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # verify payment signature
        amount = razor_pay_transaction.amount
        currency = razor_pay_transaction.currency

        verify_payment = RazorPay(amount=amount, currency=currency)
        capture = verify_payment.capture_payment(payment_id)

        # FOR DEBUGGIN PUROSES
        log_error(
            LOGGER_LOW_SEVERITY, "CaptureRazorpayPayment:Capture response", capture
        )
        # PENDING: CHECK RESPONSE FROM RAZORPAY

        # check and create user and case if not exist
        data = {
            "email": razor_pay_transaction.user_order_details.email,
            "plan": razor_pay_transaction.plan_id,
        }
        try:
            user_case_create = create_user_and_case(**data)
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "CaptureRazorpayPayment:create_user_and_case",
                "",
                description=str(err),
            )
            response["status"] = 0
            response["message"] = str(err)
            return Response(response, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(response, status.HTTP_200_OK)
