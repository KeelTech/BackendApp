from django.core.exceptions import ObjectDoesNotExist

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

    def create_transaction(self, webhook_payment_identifier, frontend_payment_identifier, **kwargs):
        if not self._order_id:
            raise ValueError("None order id while in create transaction")
        transaction_obj = Transaction.objects.create(
            frontend_payment_clients_unique_id=frontend_payment_identifier, webhook_payment_clients_unique_id=webhook_payment_identifier,
            order=Order.objects.get(pk=self._order_id))
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
