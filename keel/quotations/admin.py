from django.contrib import admin
from .models import Quotation, QuotationMilestone
class QuotationMilestoneLine(admin.TabularInline):
    model = QuotationMilestone

class QuotationAdmin(admin.ModelAdmin):

    list_display = ('q_id', 'user', 'plan', 'total_amount', 'status')
    autocomplete_fields = ('user', 'plan')
    search_fields = ('q_id', )
    readonly_fields = ('deleted_at',)
    inlines = [QuotationMilestoneLine]



admin.site.register(Quotation, QuotationAdmin)
admin.site.register(QuotationMilestone)
