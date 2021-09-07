from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from keel.cases.models import Case
from keel.payment.models import CasePaymentProfile
from keel.plans.models import Plan, Service
from keel.quotations.models import QuotationMilestone


class PaymentProfile:
    def __init__(self):
        self._order_items = None
        self._case_id = None
        self._case_model_obj = None

    def update_payment_profile(self, order_items):
        if not (self._case_id and self._order_items):
            raise ValueError("Case/order items not present")
        self._order_items = order_items
        with transaction.atomic():
            self._case_model_obj = Case.objects.get(pk=self._case_id)
            for order_item in order_items:
                item_obj = order_item.item
                if isinstance(item_obj, Service):
                    self.update_service_payment_profile(item_obj)
                elif isinstance(item_obj, (Plan, QuotationMilestone)):
                    self.update_plan_payment_profile(item_obj)

    def update_plan_payment_profile(self, item_obj):
        entity_type = ContentType.objects.get_for_model(item_obj)
        payment_profiles = CasePaymentProfile.objects.filter(is_active=True, entity_type=entity_type, entity_id=item_obj.pk)
        if not payment_profiles:
            case = Case.objects.get(pk=self._case_id)
            payable_amount = item_obj.get_payment_amount()
            total_amount = item_obj.get_total_amount()
            CasePaymentProfile.objects.create(
                case=case, entity=item_obj, total_initial_amount=total_amount, total_paid_amount=payable_amount,
                fully_paid=(total_amount == payable_amount)
            )
        else:
            payment_profile = payment_profiles[0]
            payable_amount = item_obj.get_payment_amount()
            paid_amount = payment_profile.total_paid_amount

    def update_service_payment_profile(self, item_obj):
        pass
