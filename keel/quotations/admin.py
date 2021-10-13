import logging

from django.contrib import admin
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
    readonly_fields = ('qm_id', )

class QuotationAdmin(admin.ModelAdmin):

    list_display = ('q_id', 'user', 'plan', 'total_amount', 'status')
    autocomplete_fields = ('user', 'plan')
    search_fields = ('q_id', )
    readonly_fields = ('deleted_at', 'q_id')
    inlines = [QuotationMilestoneLine]


class QuotationMilestioneAdmin(CustomBaseModelAdmin):
    
    def save_model(self, request, obj, form, change):
        id = str(obj.pk)
        customer = obj.quotation.user
        
        try:
            case = Case.objects.get(user=customer)
        except Exception as e:
            logger.error('ERROR: QUOTATIONS:QuotationMilestioneAdmin ' + str(e)) 
            return super().save_model(request, obj, form, change)
        
        payment_manager = PaymentManager()
        data = {
                "order_items": {
                    "quotation_milestone":[id],
                    "plan": [],
                    "service": []
                }
            }
        try:
            payment_details = payment_manager.generate_payment_details(
                StructNewPaymentDetailArgs(customer_id=customer.pk, customer_currency="usd",
                                           initiator_id=customer.pk, payment_client_type=PAYMENT_CLIENT_TYPE,
                                           case_id=case),
                data["order_items"]
            )
            print(payment_details)
        except ValueError as err:
            logger.error('ERROR: QUOTATIONS:QuotationMilestioneAdmin ' + str(e))
        except Exception as err:
            logger.error('ERROR: QUOTATIONS:QuotationMilestioneAdmin ' + str(e))
        return super().save_model(request, obj, form, change)

admin.site.register(Quotation, QuotationAdmin)
admin.site.register(QuotationMilestone, QuotationMilestioneAdmin)
