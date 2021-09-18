from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Transaction, Order, CasePaymentProfile


class OrderAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'customer', 'initiator', 'case', 'payment_client_type', 'total_amount', 'status')


class TransactionAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'webhook_payment_clients_unique_id', 'order', 'status')


class CasePaymentProfileAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'case', 'entity', 'total_initial_amount', 'total_paid_amount', 'fully_paid')


admin.site.register(Order, OrderAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CasePaymentProfile, CasePaymentProfileAdmin)
