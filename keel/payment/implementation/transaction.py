from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

from keel.payment.models import Transaction, Order


class PaymentTransaction(object):

    def __init__(self, order_id=None):
        self._order_id = order_id
        self._pk = None
        self._transaction_model_obj = None

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, order_id):
        self._order_id = order_id

    def create_transaction(self, webhook_payment_identifier, frontend_payment_identifier, amount, currency, **kwargs):
        if not self._order_id:
            raise ValueError("None order id while in create transaction")
        transaction_obj = Transaction.objects.create(
            frontend_payment_clients_unique_id=frontend_payment_identifier, webhook_payment_clients_unique_id=webhook_payment_identifier,
            order=Order.objects.get(pk=self._order_id), refund_amount_left=amount, currency=currency)
        return transaction_obj.id

    def complete(self):
        self._transaction_model_obj.status = Transaction.STATUS_COMPLETED
        self._transaction_model_obj.save()

    def validate_transaction_id(self, identifier):
        self._transaction_model_obj = Transaction.objects.get(webhook_payment_clients_unique_id=identifier,
                                                              status=Transaction.STATUS_PENDING)
        self._pk = identifier
        self._order_id = self._transaction_model_obj.order.id

    def get_order_transaction_details(self, order_objs):
        return Transaction.objects.filter(order__in=order_objs)

    def get_case_refund_transaction(self, case_model_obj):
        return Transaction.objects.select_for_update().filter(
            status=Transaction.STATUS_COMPLETED, refund_amount_left__gt=Decimal(0), order__case=case_model_obj).\
            order_by("-refund_amount_left")

    def update_left_over_refund_amount(self, payment_transaction_model_obj, refunded_amount):
        payment_transaction_model_obj.refund_amount_left = F("refund_amount_left") - refunded_amount
        payment_transaction_model_obj.save(update_fields=["refund_amount_left"])
