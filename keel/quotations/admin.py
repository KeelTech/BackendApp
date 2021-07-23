from django.contrib import admin
from .models import Quotation, QuotationMilestone

# Register your models here.
admin.site.register(Quotation)
admin.site.register(QuotationMilestone)
