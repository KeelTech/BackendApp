from decimal import Decimal
from typing import NamedTuple

from django.core.exceptions import ObjectDoesNotExist

from keel.authentication.models import User
from keel.payment.models import Order, OrderItem, ORDER_ITEM_MODEL_MAPPING
from keel.payment.constants import ORDER_ITEM_QUOTATION_TYPE, ORDER_ITEM_SERVICE_TYPE, ORDER_ITEM_PLAN_TYPE
from keel.plans.models import Plan, Service
from keel.quotations.models import QuotationMilestone
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_LOW_SEVERITY
from keel.cases.models import Case

import logging
logger = logging.getLogger('app-logger')


class StructOrder(NamedTuple):
    customer_id: str
    initiator_id: str
    case_id: str
    order_id: str


class IPaymentOrder(object):
    def create(self, customer_id, initiator_id, case_id):
        raise NotImplementedError

    def complete(self, order_id):
        raise NotImplementedError

    def cancel(self, order_id):
        raise NotImplementedError


class PaymentOrder(IPaymentOrder):
    def __init__(self, customer_id=None, order_id=None):
        self._customer_id = customer_id
        self._order_id = order_id
        self._initiator_id = None
        self._case_id = None
        self._order_model_obj = None
        self._related_plan_id = None

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def case_id(self):
        return self._case_id

    @case_id.setter
    def case_id(self, value):
        self._case_id = value

    @property
    def related_plan_id(self):
        if not self._related_plan_id:
            self._related_plan_id = self._try_get_related_plan_id()
        return self._related_plan_id

    def _is_valid_item_structure(self, item_list):
        for key, ids in item_list.items():
            validator = VALIDATOR_FACTORY.get_validator(key)
            if not validator.validate_item(ids):
                return False
        return True

    def _get_users_obj(self):
        user_objs = User.objects.filter(id__in=(self._customer_id, self._initiator_id))
        customer_obj = None
        initiator_obj = None
        for obj in user_objs:
            if self._customer_id == obj.id:
                customer_obj = obj
            if self._initiator_id == obj.id:
                initiator_obj = obj
        return customer_obj, initiator_obj

    def create(self, customer_id, initiator_id, item_list, case_id=None):
        self._customer_id = customer_id
        self._initiator_id = initiator_id
        self._case_id = case_id
        total_amount = Decimal(0.00)
        order_items = []
        if not self._is_valid_item_structure(item_list):
            raise ValueError("Invalid item details")
        for key, ids in item_list.items():
            item_objs = ORDER_ITEM_MODEL_MAPPING[key].objects.filter(pk__in=ids)
            for item_obj in item_objs:
                total_amount += Decimal(item_obj.get_total_amount())
                order_items.append(OrderItem.objects.create(item=item_obj, amount=item_obj.get_total_amount()))
        customer_obj, initiator_obj = self._get_users_obj()
        case_obj = Case.objects.get(id=self._case_id) if self._case_id else None
        order = Order.objects.create(
            customer=customer_obj, initiator=initiator_obj, case=case_obj, total_amount=total_amount)
        order.order_items.add(*order_items)
        self._order_id = order.id
        return self._order_id, total_amount

    def complete(self, order_id):
        self._order_id = order_id
        order_model_obj = Order.objects.select_for_update().get(pk=order_id)
        order_model_obj.status = Order.STATUS_COMPLETED
        order_model_obj.save()
        self._case_id = order_model_obj.case.id if order_model_obj.case else None
        self._customer_id = order_model_obj.customer.id
        self._order_model_obj = order_model_obj

    def cancel(self, order_id):
        pass

    def _try_get_plan_from_order_items(self, order_items):
        plan = None
        for item in order_items:
            try:
                plan = item.content_object.get_plan()
                if plan:
                    break
            except Exception as err:
                err_msg = "GetPlan not implemented for item - {} with error - {}".format(item, err)
                logger.info(logging_format(LOGGER_LOW_SEVERITY, "PaymentOrder._try_get_plan_from_order_items", "",
                                           description=err_msg))
        return plan.id

    def _try_get_related_plan_id(self):
        # 1. If we have case in order
        # 2. if we have anything related to plan in order items
        # 3. else return None
        if not self._order_id:
            return None
        order_model_obj = Order.objects.get(pk=self._order_id) if not self._order_model_obj else self._order_model_obj
        if order_model_obj.case:
            return order_model_obj.case.plan.id

        return self._try_get_plan_from_order_items(order_model_obj.order_items)

    def create_update_payment_profile(self):
        if not self._order_id:
            return None
        order_model_obj = Order.objects.get(pk=self._order_id) if not self._order_model_obj else self._order_model_obj
        for order_item in order_model_obj.order_items:
            if isinstance(order_item.item, Plan) or isinstance(order_item.item, QuotationMilestone):
                pass


class OrderItemValidators:
    def validate_item(self, items):
        raise NotImplementedError("OrderItemValidator.validate_item is not implemented")


class QuotationItemValidator(OrderItemValidators):
    def validate_item(self, items):
        quotations = QuotationMilestone.objects.filter(pk__in=items).values("pk")
        if len(items) != len(quotations):
            err_msg = "Invalid quotationMilestone id among - {}".format(set(items) - set(quotations))
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "QuotationItemValidator.validate_time", "", description=err_msg))
            return False
        return True


class PlanItemValidator(OrderItemValidators):
    def validate_item(self, items):
        plans = Plan.objects.filter(pk__in=items).values("pk")
        if len(items) != len(plans):
            err_msg = "Invalid Plan id among - {}".format(set(items) - set(plans))
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PlanItemValidator.validate_time", "", description=err_msg))
            return False
        return True


class ServiceItemValidator(OrderItemValidators):
    def validate_item(self, items):
        services = Service.objects.filter(pk__in=items).values("pk")
        if len(items) != len(services):
            err_msg = "Invalid quotationMilestone id among - {}".format(set(items) - set(services))
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "ServiceItemValidator.validate_time", "", description=err_msg))
            return False
        return True


class OrderItemValidatorFactory:
    _validator_type_mapping = {
        ORDER_ITEM_QUOTATION_TYPE: QuotationItemValidator(),
        ORDER_ITEM_PLAN_TYPE: PlanItemValidator(),
        ORDER_ITEM_SERVICE_TYPE: ServiceItemValidator()
    }

    def get_validator(self, item_type):
        return self._validator_type_mapping.get(item_type, OrderItemValidators())


VALIDATOR_FACTORY = OrderItemValidatorFactory()
