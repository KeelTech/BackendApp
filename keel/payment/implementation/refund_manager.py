from django.db import transaction

from .order import PaymentOrder
from .pay_manager import PAYMENT_CLIENT_FACTORY
from .refund_transaction import RefundTransactionHelper
from .transaction import PaymentTransaction

from keel.authentication.models import User
from keel.cases.models import Case
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY
from keel.Core.err_log import logging_format

import logging
logger = logging.getLogger('app-logger')


class RefundPaymentManager:
    def __init__(self, case_id=None, refund_amount=None, currency=None):
        self._transaction_helper = PaymentTransaction()
        self._order_helper = PaymentOrder()
        self._refund_transaction_helper = RefundTransactionHelper()
        self._case_id = case_id
        self._case_model_obj = None
        self._refund_amount = refund_amount
        self._customer_id = None
        self._customer_model_obj = None
        self._initiator_id = None
        self._initiator_model_obj = None
        self._currency = currency

    def _validate_refund_request(self):
        self._validate_customer_case()
        self._validate_case_amount()

    def _validate_customer_case(self):
        pass

    def _validate_case_amount(self):
        pass

    def _create_refund_amount_transaction_objs(self, transaction_details):
        sorted_transactions = sorted(transaction_details, key=lambda k: k["refund_amount_left"])
        refund_amount_transaction_list = []
        amount_to_be_refunded = self._refund_amount
        for transaction_detail in sorted_transactions:
            if amount_to_be_refunded <= 0:
                break
            refund_amount_from_transaction = min(amount_to_be_refunded, transaction_detail['refund_amount_left'])
            payment_transaction_model_obj = transaction_detail['transaction_model_obj']
            self._transaction_helper.update_left_over_refund_amount(
                payment_transaction_model_obj, refund_amount_from_transaction)
            refund_amount_transaction_list.append(self._refund_transaction_helper.create_refund_amount_transaction(
                payment_transaction_model_obj, transaction_detail['client_type'],
                refund_amount_from_transaction, transaction_detail['currency']
            ))
            amount_to_be_refunded = amount_to_be_refunded - refund_amount_from_transaction
        return refund_amount_transaction_list

    def _initiate_client_side_refund(self, refund_amount_transaction_model_objs):
        all_refunds_triggered = True
        for obj in refund_amount_transaction_model_objs:
            try:
                refund_client = PAYMENT_CLIENT_FACTORY.try_get_refund_client(obj.payment_client_type)
                refund_intent_response = refund_client.refund_payment_intent(
                    obj.transaction.webhook_payment_clients_unique_id, obj.amount)
                if not refund_intent_response["status"]:
                    error_msg = "Error getting triggering refund for client type - {}, user - {}, case - {}, " \
                                "amount - {}, transaction id - {} by initiator id - {} with error - " \
                                "{}".format(obj.payment_client_type, obj.transaction.order.customer, obj.transaction.order.case,
                                            obj.amount, obj.transaction.pk, self._initiator_model_obj, err)
                    logger.error(logging_format(
                        LOGGER_CRITICAL_SEVERITY, "RefundPaymentManager:_initiate_client_side_refund", self._initiator_id,
                        description=error_msg))
                self._refund_transaction_helper.update_client_refund_identifier(
                    obj, refund_intent_response["data"]["client_identifier"])
            except KeyError as err:
                error_msg = "Error getting client type from client factory for client type - {}, user - {}, case - {}, " \
                            "amount - {}, transaction id - {} by initiator id - {} with error - " \
                            "{}".format(obj.payment_client_type, obj.transaction.order.customer, obj.transaction.order.case,
                                        obj.amount, obj.transaction.pk, self._initiator_model_obj, err)
                logger.error(logging_format(
                    LOGGER_CRITICAL_SEVERITY, "RefundPaymentManager:_initiate_client_side_refund", self._initiator_id,
                    description=error_msg))
                all_refunds_triggered = False
            except ValueError as err:
                error_msg = "Error while initiating refund for client type - {}, user - {}, case - {}, amount - {}, " \
                            "transaction id - {} by initiator id - {} with error - {}".format(obj.payment_client_type,
                                                                                              obj.transaction.order.customer,
                                                                                              obj.transaction.order.case,
                                                                                              obj.amount, obj.transaction.pk,
                                                                                              self._initiator_model_obj, err)
                logger.error(logging_format(
                    LOGGER_CRITICAL_SEVERITY, "RefundPaymentManager:_initiate_client_side_refund", self._initiator_id,
                    description=error_msg))
                all_refunds_triggered = False
            except Exception as err:
                error_msg = "Error while initiating refund for client type - {}, user - {}, case - {}, amount - {}, " \
                            "transaction id - {} by initiator id - {} with error - {}".format(obj.payment_client_type,
                                                                                              obj.transaction.order.customer,
                                                                                              obj.transaction.order.case,
                                                                                              obj.amount, obj.transaction.pk,
                                                                                              self._initiator_model_obj, err)
                logger.error(logging_format(
                    LOGGER_CRITICAL_SEVERITY, "RefundPaymentManager:_initiate_client_side_refund", self._initiator_id,
                    description=error_msg))
                all_refunds_triggered = False

        return all_refunds_triggered

    def _trigger_case_refund(self):
        with transaction.atomic():
            self._case_model_obj = Case.objects.select_for_update().get(pk=self._case_id)
            transaction_details = self._transaction_helper.get_case_refund_transaction(self._case_model_obj)
            refund_amount_transaction_list = self._create_refund_amount_transaction_objs(transaction_details)
            refund_transaction_model_obj = self._refund_transaction_helper.create_refund_transaction(
                self._customer_model_obj, self._initiator_model_obj, self._case_model_obj, self._refund_amount,
                self._currency, refund_amount_transaction_list)
            all_refunds_triggered = self._initiate_client_side_refund(refund_amount_transaction_list)
            self._refund_transaction_helper.update_refund_transaction_state(all_refunds_triggered)
        return refund_transaction_model_obj.pk

    def initiate_refund(self, initiator_id, case_id, refund_amount):
        self._initiator_id = initiator_id
        self._initiator_model_obj = User.objects.get(pk=initiator_id)
        self._case_id = case_id
        self._case_model_obj = Case.objects.get(pk=case_id, is_active=True)
        self._customer_model_obj = self._case_model_obj.user
        self._refund_amount = refund_amount
        self._validate_refund_request()
        refund_transaction_id = self._trigger_case_refund()
        return refund_transaction_id

    def refund_webhook_event_handler(self, payment_client_type, webhook_payload, signature):
        pass

