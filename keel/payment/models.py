import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from keel.authentication.models import User
from keel.cases.models import Case
from keel.Core.models import SoftDeleteModel, TimeStampedModel
from keel.payment.constants import (ORDER_ITEM_PLAN_TYPE,
                                    ORDER_ITEM_QUOTATION_TYPE,
                                    ORDER_ITEM_SERVICE_TYPE)
from keel.plans.models import Plan, Service
from keel.quotations.models import QuotationMilestone

ORDER_ITEM_MODEL_MAPPING = {
    ORDER_ITEM_QUOTATION_TYPE: QuotationMilestone,
    ORDER_ITEM_PLAN_TYPE: Plan,
    ORDER_ITEM_SERVICE_TYPE: Service,
}


class OrderItem(TimeStampedModel, SoftDeleteModel):
    item_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    item_id = models.CharField(max_length=512)
    item = GenericForeignKey("item_type", "item_id")
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return str(self.item_id)


class Order(TimeStampedModel, SoftDeleteModel):
    STATUS_PENDING = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    PAYMENT_CLIENT_STRIPE = 1
    PAYMENT_CLIENT_CHOICE = {(PAYMENT_CLIENT_STRIPE, "Stripe")}

    customer = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="customer_order"
    )
    initiator = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="initiator_order"
    )
    case = models.ForeignKey(Case, on_delete=models.DO_NOTHING, null=True)
    order_items = models.ManyToManyField(OrderItem)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, null=True, blank=True, default=None)
    payment_client_type = models.PositiveSmallIntegerField(
        choices=PAYMENT_CLIENT_CHOICE, default=PAYMENT_CLIENT_STRIPE
    )

    class Meta:
        db_table = "order"

    def __str__(self):
        return str(self.customer)


class Transaction(TimeStampedModel, SoftDeleteModel):
    STATUS_PENDING = 1
    STATUS_COMPLETED = 2
    STATUS_CANCELLED = 3
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frontend_payment_clients_unique_id = models.CharField(max_length=1024, unique=True)
    webhook_payment_clients_unique_id = models.CharField(max_length=1024, unique=True)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    class Meta:
        db_table = "transaction"

    def __str__(self):
        return str(self.id)


class CasePaymentProfile(TimeStampedModel, SoftDeleteModel):

    case = models.ForeignKey(Case, on_delete=models.DO_NOTHING)

    entity_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    entity_id = models.CharField(max_length=512)
    entity = GenericForeignKey("entity_type", "entity_id")

    # payment_client = models.PositiveSmallIntegerField(choices=PAYMENT_CLIENT_CHOICE, default=PAYMENT_CLIENT_STRIPE)
    total_initial_amount = models.DecimalField(
        verbose_name="Amount of Plan/Service taken by customer",
        max_digits=12,
        decimal_places=2,
    )
    total_paid_amount = models.DecimalField(
        verbose_name="Total amount paid in instalment till now",
        max_digits=12,
        decimal_places=2,
    )
    fully_paid = models.BooleanField(
        verbose_name="Amount fully paid for the plan/service", default=False
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_case_payment_profile"

    def __str__(self) -> str:
        return str(self.case)


class UserOrderDetails(TimeStampedModel):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return str(self.email)


class RazorPayTransactions(TimeStampedModel):
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    user_order_details = models.ForeignKey(
        UserOrderDetails,
        on_delete=models.DO_NOTHING,
        related_name="user_razorpay_transactions",
    )
    amount = models.CharField(max_length=50, null=True, blank=True)
    # plan_type = models.CharField(max_length=512, null=True, blank=True)
    plan_id = models.ForeignKey(Plan, on_delete=models.DO_NOTHING, null=True, blank=True)
    order_id = models.CharField(max_length=512, null=True, blank=True)
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    partial_payment = models.BooleanField(default=False)
    currency = models.CharField(max_length=5, null=True, blank=True)