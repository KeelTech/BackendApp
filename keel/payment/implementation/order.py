from decimal import Decimal
from typing import NamedTuple

from django.core.exceptions import ObjectDoesNotExist

from keel.authentication.models import User
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY, LOGGER_LOW_SEVERITY
from keel.cases.implementation.case_util_helper import CaseUtilHelper
from keel.cases.models import Case
from keel.payment.models import Order, OrderItem, ORDER_ITEM_MODEL_MAPPING
from keel.payment.constants import ORDER_ITEM_QUOTATION_TYPE, ORDER_ITEM_SERVICE_TYPE, ORDER_ITEM_PLAN_TYPE, DEFAULT_CURRENCY
from keel.plans.models import Plan, Service
from keel.plans.implementation.plan_util_helper import PlanUtilHelper
from keel.quotations.models import QuotationMilestone

import logging
logger = logging.getLogger('app-logger')


class StructOrder(NamedTuple):
    customer_id: str
    initiator_id: str
    case_id: str
    order_id: str


class IPaymentOrder(object):
    def create(self, customer_id, initiator_id, item_list, payment_client_type, case_id=None):
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
        self._payment_client_type = None
        self._plan_util_helper = PlanUtilHelper()
        self._case_util_helper = CaseUtilHelper()

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def order_id(self):
        return self._order_id

    @property
    def order_items(self):
        return self._order_model_obj.order_items.all()

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

    @property
    def order_model_obj(self):
        self._order_model_obj = Order.objects.get(pk=self._order_id) if not self._order_model_obj and self._order_id else self._order_model_obj
        return self._order_model_obj

    def _is_valid_item_structure(self, item_list):
        any_item_available = False
        for key, ids in item_list.items():
            validator = VALIDATOR_FACTORY.get_validator(key)
            any_item_available = True if any_item_available or ids else False
            if ids and (not validator or not validator.validate_item(ids, self._customer_id, self.case_id)):
                return False
        return any_item_available

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

    def _try_get_plan_from_order_items(self, order_items):
        plan = None
        for order_item in order_items:
            try:
                plan = order_item.item.get_plan()
                if plan:
                    break
            except Exception as err:
                err_msg = "GetPlan not implemented for item - {} with error - {}".format(order_item, err)
                logger.info(logging_format(LOGGER_LOW_SEVERITY, "PaymentOrder._try_get_plan_from_order_items", "",
                                           description=err_msg))
        return plan.id

    def _try_get_related_plan_id(self):
        # 1. If we have case in order
        # 2. if we have anything related to plan in order items
        # 3. else return None
        if not self._order_id:
            return None
        order_model_obj = self.order_model_obj
        return self._try_get_plan_from_order_items(order_model_obj.order_items.all())

    def _get_or_create_case(self, order_model_items, currency):
        if not self._case_id:
            for model_item in order_model_items:
                self._case_id = model_item.item.get_case()
                if self._case_id:
                    break
        if self._case_id:
            case_model_obj = Case.objects.get(pk=self._case_id, is_active=True)
        else:
            customer_model_obj = User.objects.select_for_update().get(pk=self._customer_id)
            case_model_obj = self._case_util_helper.create_with_free_plan(customer_model_obj, currency)
        self._case_id = case_model_obj.pk
        return case_model_obj

    def _update_case_order_items(self, order_items, case_obj):
        for order in order_items:
            order.item.update_case(case_obj)

    def _create_order_items(self, item_list):
        currency = DEFAULT_CURRENCY
        order_item_model_objs = []
        total_payable_amount = Decimal(0.0)
        for key, ids in item_list.items():
            if not ids:
                continue
            item_objs = ORDER_ITEM_MODEL_MAPPING[key].objects.filter(pk__in=ids)
            for item_obj in item_objs:
                item_payable_amount = Decimal(item_obj.get_payment_amount())
                total_payable_amount = total_payable_amount + item_payable_amount
                order_item_model_objs.append(OrderItem.objects.create(item=item_obj, amount=item_payable_amount))
                currency = item_obj.get_currency() or currency
        return order_item_model_objs, total_payable_amount, currency

    def _complete_order_items(self):
        for order in self._order_model_obj.order_items.all():
            order.item.complete_payment()

    def create(self, customer_id, initiator_id, item_list, payment_client_type, case_id=None):
        self._customer_id = customer_id
        self._initiator_id = initiator_id
        self._payment_client_type = payment_client_type
        self._case_id = case_id

        if not self._is_valid_item_structure(item_list):
            raise ValueError("Invalid item details")
        order_item_model_objs, total_payable_amount, currency = self._create_order_items(item_list)
        customer_model_obj, initiator_model_obj = self._get_users_obj()
        case_model_obj = self._get_or_create_case(order_item_model_objs, currency)
        self._update_case_order_items(order_item_model_objs, case_model_obj)
        order_model_obj = Order.objects.create(
            customer=customer_model_obj, initiator=initiator_model_obj, case=case_model_obj, total_amount=total_payable_amount,
            payment_client_type=payment_client_type, currency=currency)
        order_model_obj.order_items.add(*order_item_model_objs)
        self._order_id = order_model_obj.pk
        return self._order_id, total_payable_amount, currency

    def complete(self, order_id):
        self._order_id = order_id
        order_model_obj = Order.objects.select_for_update().get(pk=order_id, status=Order.STATUS_PENDING)
        order_model_obj.status = Order.STATUS_COMPLETED
        order_model_obj.save()
        self._order_model_obj = order_model_obj
        self._complete_order_items()
        self._case_id = order_model_obj.case.pk if order_model_obj.case else None
        self._customer_id = order_model_obj.customer.id
        self._order_model_obj = order_model_obj

    def cancel(self, order_id):
        pass

    def get_pending_customer_orders(self, customer_id):
        return Order.objects.filter(customer=customer_id, status=Order.STATUS_PENDING)

    def get_order_items_details(self, order_items):
        item_details = []
        for order_item in order_items:
            item_detail = {
                "payable_amount": order_item.item.get_payment_amount(),
                "total_amount": order_item.item.get_total_amount()
            }
            plan_model_obj = order_item.item.get_plan()
            if plan_model_obj:
                item_detail.update({
                    "plan_details": self._plan_util_helper.get_plan_details(plan_model_obj)
                })
            item_details.append(item_detail)
        return item_details

    def update_order_case(self, case_model_obj):
        self._order_model_obj.case = case_model_obj
        self._order_model_obj.save()

    def get_order_details(self, order_model_obj):
        return {
            "customer_id": order_model_obj.customer.pk,
            "initiator_id": order_model_obj.initiator.pk,
            "order_items": self.get_order_items_details(order_model_obj.order_items.all()),
            "status": order_model_obj.status,
            "payable_amount": order_model_obj.total_amount,
            "currency": order_model_obj.currency,
        }


class OrderItemValidators:
    def validate_item(self, items, user_id, case_id=None):
        raise NotImplementedError("OrderItemValidator.validate_item is not implemented")


class QuotationItemValidator(OrderItemValidators):
    def validate_item(self, items, user_id, case_id=None):
        milestones = QuotationMilestone.objects.filter(pk__in=items, quotation__user__pk=user_id).values("pk", "quotation")
        if len(items) != len(milestones):
            quotation_ids = set([milestone['pk'] for milestone in milestones])
            err_msg = "Invalid quotationMilestone id among - {}".format(set(items) - quotation_ids)
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "QuotationItemValidator.validate_time", "", description=err_msg))
            return False

        if case_id:
            for milestone in milestones:
                milestone_case = milestone.get_case()
                if milestone_case and milestone_case.pk != case_id:
                    err_msg = "QuotationMilestone case id - {} mismatch with given case id - {}".format(milestone_case.pk, case_id)
                    logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "QuotationItemValidator.validate_time", user_id, description=err_msg))
                    return False
        return True


class PlanItemValidator(OrderItemValidators):
    def validate_item(self, items, user_id=None, case_id=None):
        plans = Plan.objects.filter(pk__in=items).values("pk")
        if len(items) != len(plans):
            err_msg = "Invalid Plan id among - {}".format(set(items) - set(plans))
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PlanItemValidator.validate_time", "", description=err_msg))
            return False
        return True


class ServiceItemValidator(OrderItemValidators):
    def validate_item(self, items, user_id=None, case_id=None):
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
