import re

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
import nested_admin
from keel.authentication.models import SPOCDetails, DoctorNumber
from .forms import SPOCDetailsForm
from reversion.admin import VersionAdmin
from django import forms
from keel.doctor import models as doc_models
from dal import autocomplete


# class BillingAccountInline(GenericTabularInline, nested_admin.NestedTabularInline):
#     form = BillingAccountForm
#     formset = BillingAccountFormSet
#     can_delete = False
#     extra = 0
#     model = BillingAccount
#     show_change_link = False
#     readonly_fields = ['merchant_id']
#     fields = ['merchant_id', 'type', 'account_number', 'ifsc_code', 'pan_number', 'pan_copy', 'account_copy', 'enabled']


class SPOCDetailsInline(GenericTabularInline):
    can_delete = True
    extra = 0
    form = SPOCDetailsForm
    model = SPOCDetails
    show_change_link = False
    fields = ['name', 'std_code', 'number', 'email', 'details', 'contact_type']


class DoctorNumberForm(forms.ModelForm):
    dn = DoctorNumber.objects.values_list('doctor', flat=True)
    doctor = forms.ModelChoiceField(
        queryset=doc_models.Doctor.objects.exclude(id__in=dn),
        widget=autocomplete.ModelSelect2(url='docnumber-autocomplete')
    )

    class Meta:
        model = DoctorNumber
        fields = ('phone_number', 'doctor')


class DoctorNumberAdmin(VersionAdmin):
    list_display = ('phone_number', 'doctor', 'hospital', 'updated_at')
    search_fields = ['phone_number', 'doctor__name', 'hospital__name']
    date_hierarchy = 'created_at'
    # form = DoctorNumberForm
    autocomplete_fields = ['doctor']
    # list_display_links = None

    # def has_add_permission(self, request, obj=None):
    #     return False

admin.site.register(DoctorNumber, DoctorNumberAdmin)
