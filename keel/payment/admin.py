from django.contrib import admin
from keel.Core.admin import CustomBaseModelAdmin
from .models import Transaction, Order


class OrderAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'customer', 'initiator', 'case', 'payment_client_type', 'total_amount', 'status')


class TransactionAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'payment_clients_unique_id', 'order', 'status')


admin.site.register(Order, OrderAdmin)
admin.site.register(Transaction, TransactionAdmin)
