from keel.payment.models import RefundAmountTransaction, RefundTransaction
from .transaction import PaymentTransaction


class RefundTransactionHelper:
    def __init__(self):
        self._transaction_helper_obj = PaymentTransaction()
        self._payment_transaction_id = None
        self._order_id = None
        self._refund_transaction_model_obj = None

    def create_refund_amount_transaction(self, transaction_model_obj, payment_client_type, amount, currency):
        return RefundAmountTransaction.objects.create(
            transaction=transaction_model_obj, amount=amount, currency=currency, payment_client_type=payment_client_type
        )

    def update_initiated_status(self, payment_transaction_id):
        return RefundAmountTransaction.objects.filter(pk=payment_transaction_id).update(status=RefundAmountTransaction.STATUS_INITIATED)

    def create_refund_transaction(self, customer_model_obj, initiator_model_obj, case_model_obj, amount, currency,
                                  payment_transaction_model_objs):
        self._refund_transaction_model_obj = RefundTransaction.objects.create(
            customer=customer_model_obj, initiator=initiator_model_obj,
            case=case_model_obj, refund_amount=amount, currency=currency)
        self._refund_transaction_model_obj.payment_transactions.add(*payment_transaction_model_objs)
        return self._refund_transaction_model_obj

    def update_client_refund_identifier(self, refund_amount_transaction_model_obj, client_identifier):
        refund_amount_transaction_model_obj.webhook_payment_clients_identifier = client_identifier
        refund_amount_transaction_model_obj.status = RefundAmountTransaction.STATUS_INITIATED
        refund_amount_transaction_model_obj.save()

    def update_refund_transaction_state(self, refund_transaction_status):
        self._refund_transaction_model_obj.status = refund_transaction_status
        self._refund_transaction_model_obj.save()

    def get_refund_triggered_status(self, total_transaction_count, triggered_transaction_count):
        if triggered_transaction_count == 0:
            return RefundTransaction.STATUS_PENDING
        elif triggered_transaction_count == total_transaction_count:
            return RefundTransaction.STATUS_INITIATED
        elif triggered_transaction_count < total_transaction_count:
            return RefundTransaction.STATUS_PARTIAL_INITIATED

    def create_refund_amount_transaction_objs(self, transaction_model_objs, refund_amount):
        refund_amount_transaction_list = []
        for transaction_model_obj in transaction_model_objs:
            if refund_amount <= 0:
                break
            refund_amount_from_transaction = min(refund_amount, transaction_model_obj.refund_amount_left)
            self._transaction_helper_obj.update_left_over_refund_amount(
                transaction_model_obj, refund_amount_from_transaction)
            refund_amount_transaction_list.append(self.create_refund_amount_transaction(
                transaction_model_obj, transaction_model_obj.order.payment_client_type,
                refund_amount_from_transaction, transaction_model_obj.currency
            ))
            refund_amount = refund_amount - refund_amount_from_transaction
        return refund_amount_transaction_list
