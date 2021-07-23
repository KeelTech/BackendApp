from django.contrib import admin
from .models import Quotation, QuotationMilestone

class QuotationAdmin(admin.ModelAdmin):

    list_display = ('q_id', 'user', 'plan', 'total_amount', 'status')
    autocomplete_fields = ('user', 'plan')
    search_fields = ('q_id', )
    readonly_fields = ('deleted_at',)

class QuotationMilestoneAdmin(admin.ModelAdmin):

    list_display = ('qm_id', 'due_date', 'amount', 'quotation', 'status')
    autocomplete_fields = ('quotation', )
    readonly_fields = ('deleted_at',)

admin.site.register(Quotation, QuotationAdmin)
admin.site.register(QuotationMilestone, QuotationMilestoneAdmin)
