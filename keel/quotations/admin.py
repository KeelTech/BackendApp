import logging

from django.contrib import admin
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY
from keel.cases.models import Case
from keel.Core.admin import CustomBaseModelAdmin
from keel.payment.implementation.pay_manager import (
    PaymentManager, StructNewPaymentDetailArgs)
from keel.payment.models import Order

from .models import Quotation, QuotationMilestone

logger = logging.getLogger('app-logger')

PAYMENT_CLIENT_TYPE = Order.PAYMENT_CLIENT_STRIPE

class QuotationMilestoneLine(admin.TabularInline):
    model = QuotationMilestone
    extra = 0
    readonly_fields = ('deleted_at', )

class QuotationAdmin(admin.ModelAdmin):

    list_display = ('q_id', 'user', 'plan', 'total_amount', 'status')
    autocomplete_fields = ('user', 'plan')
    search_fields = ('q_id', )
    readonly_fields = ('deleted_at', 'q_id')
    inlines = [QuotationMilestoneLine]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            customer = instance.quotation.user
            payment_manager = PaymentManager()
            order_items = {
                "quotation_milestone":[str(instance.pk)],
                "plan": [],
                "service": []
            }
            try:
                payment_details = payment_manager.generate_payment_details(
                    StructNewPaymentDetailArgs(customer_id=customer.pk, customer_currency="usd",
                                            initiator_id=request.user.pk, payment_client_type=PAYMENT_CLIENT_TYPE,
                                            case_id=None),
                    order_items
                )
            except ValueError as err:
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "QuotationAdmin.save_formset",
                                "", description=str(err)))
            except Exception as err:
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "QuotationAdmin.save_formset",
                                "", description=str(err)))
        return super().save_formset(request, form, formset, change)

class QuotationMilestioneAdmin(CustomBaseModelAdmin):

    list_display = ('qm_id', 'amount', 'status', 'due_date')
    readonly_fields = ('qm_id', 'deleted_at')


admin.site.register(Quotation, QuotationAdmin)
admin.site.register(QuotationMilestone, QuotationMilestioneAdmin)
