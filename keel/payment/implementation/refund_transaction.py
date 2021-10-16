from keel.payment.models import RefundAmountTransaction, RefundTransaction


class RefundTransactionHelper:
    def __init__(self):
        self._payment_transaction_id = None
        self._order_id = None
        self._refund_transaction_model_obj = None

    def create_refund_amount_transaction(self, transaction_model_obj, payment_client_type, amount, currency):
        return RefundAmountTransaction.objects.create()

    def update_initiated_status(self, payment_transaction_id):
        return RefundAmountTransaction.objects.filter(pk=payment_transaction_id).update(status=RefundAmountTransaction.STATUS_INITIATED)

    def create_refund_transaction(self, customer_model_obj, initiator_model_obj, case_model_obj, amount, currency,
                                  payment_transaction_model_objs):
        self._refund_transaction_model_obj = RefundTransaction.objects.create(customer=customer_model_obj, initiator=initiator_model_obj,
                                                                              case=case_model_obj, refund_amount=amount, currency=currency,
                                                                              payment_transactions=payment_transaction_model_objs)
        return self._refund_transaction_model_obj

    def update_client_refund_identifier(self, refund_amount_transaction_model_obj, client_identifier):
        refund_amount_transaction_model_obj.webhook_payment_clients_identifier = client_identifier
        refund_amount_transaction_model_obj.status = RefundAmountTransaction.STATUS_INITIATED
        refund_amount_transaction_model_obj.save()

    def update_refund_transaction_state(self, all_refunds_triggered):
        status = RefundTransaction.STATUS_PARTIAL_INITIATED if not all_refunds_triggered else RefundTransaction.STATUS_INITIATED
        self._refund_transaction_model_obj["status"] = status
        self._refund_transaction_model_obj.save()
