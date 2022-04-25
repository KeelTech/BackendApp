from django.contrib import admin
from keel.api.v1.payment.razor_payment import RazorPay
from keel.Core.admin import CustomBaseModelAdmin

from .models import (CasePaymentProfile, Order, OrderItem,
                     RazorPayTransactions, Transaction, UserOrderDetails)


class OrderAdmin(CustomBaseModelAdmin):
    list_display = (
        "id",
        "customer",
        "initiator",
        "case",
        "payment_client_type",
        "total_amount",
        "status",
    )


class TransactionAdmin(CustomBaseModelAdmin):
    list_display = ("id", "webhook_payment_clients_unique_id", "order", "status")


class CasePaymentProfileAdmin(CustomBaseModelAdmin):
    list_display = (
        "id",
        "case",
        "entity",
        "total_initial_amount",
        "total_paid_amount",
        "fully_paid",
    )


class UserOrderDetailsAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "email")


class RazorPayTransactionsAdmin(admin.ModelAdmin):
    list_display = (
        "user_order_details",
        "plan_id",
        "order_id",
        "payment_id",
        "amount",
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CasePaymentProfile, CasePaymentProfileAdmin)
admin.site.register(UserOrderDetails, UserOrderDetailsAdmin)
admin.site.register(RazorPayTransactions, RazorPayTransactionsAdmin)
