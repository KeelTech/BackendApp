from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F

from keel.cases.models import Case
from keel.payment.models import CasePaymentProfile
from keel.plans.models import Plan, Service
from keel.quotations.models import QuotationMilestone


class PaymentProfile:
    def __init__(self):
        self._order_items = None
        self._case_id = None
        self._case_model_obj = None

    @property
    def case_id(self):
        return self._case_id

    @case_id.setter
    def case_id(self, value):
        self._case_id = value

    def update_payment_profile(self, order_items):
        if not (self._case_id and order_items):
            raise ValueError("Case/order items not present")
        self._order_items = order_items
        with transaction.atomic():
            self._case_model_obj = Case.objects.select_for_update().get(pk=self._case_id)
            for order_item in order_items:
                item_obj = order_item.item
                if isinstance(item_obj, Service):
                    self._update_service_payment_profile(item_obj)
                elif isinstance(item_obj, (Plan, QuotationMilestone)):
                    self._update_plan_payment_profile(item_obj)

    def _update_plan_payment_profile(self, item_obj):
        entity_obj = item_obj.get_plan()
        payable_amount = item_obj.get_payment_amount()
        total_amount = item_obj.get_total_amount()
        self._update_entity_payment_profile(entity_obj, payable_amount, total_amount)

    def _update_service_payment_profile(self, item_obj):
        entity_obj = item_obj
        payable_amount = item_obj.get_payment_amount()
        total_amount = item_obj.get_total_amount()
        self._update_entity_payment_profile(entity_obj, payable_amount, total_amount)

    def _update_entity_payment_profile(self, entity_obj, payable_amount, total_amount):
        entity_type = ContentType.objects.get_for_model(entity_obj)
        payment_profiles = CasePaymentProfile.objects.select_for_update().filter(
            is_active=True, case__pk=self._case_id, entity_type=entity_type, entity_id=entity_obj.pk, fully_paid=False)
        if not payment_profiles:
            CasePaymentProfile.objects.create(
                case=self._case_model_obj, entity=entity_obj, total_initial_amount=total_amount,
                total_paid_amount=payable_amount, fully_paid=(total_amount == payable_amount)
            )
        else:
            payment_profile = payment_profiles[0]
            paid_amount = payment_profile.total_paid_amount
            total_amount = payment_profile.total_initial_amount
            payment_profile.total_paid_amount = F("total_paid_amount") + payable_amount
            payment_profile.fully_paid = (total_amount == paid_amount+payable_amount)
            payment_profile.save()
