from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Transaction, Order, CasePaymentProfile, OrderItem, RefundTransaction, RefundAmountTransaction


class OrderAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'customer', 'initiator', 'case', 'payment_client_type', 'total_amount', 'status')


class TransactionAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'webhook_payment_clients_unique_id', 'order', 'status')


class CasePaymentProfileAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'case', 'entity', 'total_initial_amount', 'total_paid_amount', 'fully_paid')


class RefundTransactionAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'customer', 'initiator', 'case', 'refund_amount', 'currency', 'status')


class RefundAmountTransactionAdmin(CustomBaseModelAdmin):
    list_display = ('transaction', 'amount', 'currency', 'payment_client_type', 'webhook_payment_clients_identifier', 'status')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CasePaymentProfile, CasePaymentProfileAdmin)
admin.site.register(RefundTransaction, RefundTransactionAdmin)
admin.site.register(RefundAmountTransaction, RefundAmountTransactionAdmin)
