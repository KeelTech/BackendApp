from typing import NamedTuple

from django.conf import settings
from django.db import transaction

from .order import PaymentOrder
from .transaction import PaymentTransaction
from .payment_profile import PaymentProfile
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_LOW_SEVERITY, LOGGER_CRITICAL_SEVERITY
from keel.cases.implementation.case_util_helper import CaseUtilHelper
from keel.cases.models import Case
from keel.payment.models import Order
from keel.stripe.utils import STRIPE_PAYMENT_OBJECT, STRIPE_EVENT_MANAGER

import logging
logger = logging.getLogger('app-logger')


class StructNewPaymentDetailArgs(NamedTuple):
    customer_id: str
    customer_currency: str
    initiator_id: str
    payment_client_type: str
    case_id: str


class PaymentManager(object):

    def __init__(self):
        self._order = PaymentOrder()
        self._transaction = PaymentTransaction()
        self._payment_profile = PaymentProfile()
        self._payment_client = None
        self._new_payment_args = None
        self._case_id = None
        self._payment_client_event_handler = None
        self._case_util_helper = CaseUtilHelper()

    def _trigger_create_payment(self, items_list, **kwargs):
        with transaction.atomic():
            order_id, amount, currency = self._order.create(
                self._new_payment_args.customer_id, self._new_payment_args.initiator_id, items_list,
                self._new_payment_args.payment_client_type, self._new_payment_args.case_id)
            self._transaction.order_id = order_id
            client_payment_response = self._payment_client.create_new_payment(
                amount, currency or self._new_payment_args.customer_currency)
            if not client_payment_response["status"]:
                error_msg = "Error creating new payment for client {} with error {}".format(self._payment_client, client_payment_response["error"])
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentManager:_trigger_create_payment",
                                            self._new_payment_args.customer_id, description=error_msg))
                raise ValueError("Error in Payment client api")
            transaction_id = self._transaction.create_transaction(
                client_payment_response["data"]["unique_identifier"], client_payment_response["data"]["client_secret"])
        return {
            "order_id": order_id,
            "transaction_id": transaction_id,
            "payment_unique_identifier": client_payment_response["data"]["unique_identifier"],
            "payment_client_secret": client_payment_response["data"]["client_secret"]
        }

    def generate_payment_details(self, pay_args: StructNewPaymentDetailArgs, items_list, **kwargs):
        self._new_payment_args = pay_args
        self._payment_client = PAYMENT_CLIENT_FACTORY.get_payment_client(self._new_payment_args.payment_client_type)
        payment_details = self._trigger_create_payment(items_list, **kwargs)
        # Construct payment details
        return payment_details

    def generate_payment_url(self, pay_args: StructNewPaymentDetailArgs, items_list, **kwargs):
        self._new_payment_args = pay_args
        self._payment_client = PAYMENT_CLIENT_FACTORY.get_payment_client(self._new_payment_args.payment_client_type)
        payment_details = self._trigger_create_payment(items_list, **kwargs)
        return create_payment_url(payment_details["unique_identifier"])

    def payment_webhook_event_handler(self, payment_client_type, webhook_payload, signature):
        self._payment_client_event_handler = PAYMENT_CLIENT_FACTORY.get_payment_event_client_handler(payment_client_type)
        self._payment_client_event_handler.process(self, webhook_payload, signature)

    def complete_payment_transaction(self, unique_identifier):
        with transaction.atomic():
            self._transaction.validate_transaction_id(unique_identifier)
            self._order.complete(self._transaction.order_id)
            self._transaction.complete()
            case_id = self._order.case_id
            if not case_id:
                err_msg = "Cannot complete order without Plan and Case for " \
                          "identifier - {}, order id - {} and customer " \
                          "id - {}".format(unique_identifier, self._order.order_id, self._order.customer_id)
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentManager:complete_payment_transaction",
                                            self._order.customer_id, description=err_msg))
                raise ValueError("Cannot Complete payment and create order without Plan and Case")
            related_plan_id = self._order.related_plan_id
            if related_plan_id:
                Case.objects.update_plan_agent(case_id, related_plan_id)
            self._payment_profile.case_id = case_id
            self._payment_profile.update_payment_profile(self._order.order_items)

    def cancel_payment_transaction(self, unique_identifier):
        pass

    def initialize_refund(self, case_id, amount, **kwargs):
        raise NotImplementedError

    def cancel_payment(self, case_id, order_id, **kwargs):
        raise NotImplementedError

    def get_pending_transaction(self, customer_id):
        order_objs = self._order.get_pending_customer_orders(customer_id)
        transaction_objs = self._transaction.get_order_transaction_details(order_objs)
        transaction_details = []
        for transaction_obj in transaction_objs:
            order_model_obj = transaction_obj.order
            case_model_obj = order_model_obj.case
            transaction_details.append({
                "front_end_transaction_identifier": transaction_obj.frontend_payment_clients_unique_id,
                "status": transaction_obj.status,
                "order_total_amount": order_model_obj.total_amount,
                "order_details": self._order.get_order_details(order_model_obj),
                "case_details": self._case_util_helper.get_case_details(case_model_obj),
            })
        return transaction_details


class PaymentClientFactory(object):
    payment_client_map = {
        Order.PAYMENT_CLIENT_STRIPE: STRIPE_PAYMENT_OBJECT
    }
    default_payment_client = STRIPE_PAYMENT_OBJECT

    payment_client_event_handler_map = {
        Order.PAYMENT_CLIENT_STRIPE: STRIPE_EVENT_MANAGER
    }
    default_client_event_handler = STRIPE_EVENT_MANAGER

    def get_payment_client(self, payment_client_type):
        return self.payment_client_map.get(payment_client_type) or self.default_payment_client

    def get_payment_event_client_handler(self, payment_client_type):
        return self.payment_client_event_handler_map.get(payment_client_type) or self.default_client_event_handler


def create_payment_url(unique_identifier):
    return settings.BASE_URL + "/" + unique_identifier


PAYMENT_CLIENT_FACTORY = PaymentClientFactory()
