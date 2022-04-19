import razorpay
from django.conf import settings
from keel.Core.constants import (
    LOGGER_CRITICAL_SEVERITY,
    LOGGER_LOW_SEVERITY,
    LOGGER_MODERATE_SEVERITY,
)
from keel.Core.err_log import log_error

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class RazorPay(object):
    def __init__(self, amount, currency, user, **kwargs):
        self.amount = amount
        self.currency = currency
        self.user = user

    def create_order(self):
        amount = self.amount * 1000

        try:
            order = client.order.create(dict(amount=amount, currency=self.currency))
            return order
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "RazorPay:create_order",
                self.user.id,
                description=str(err),
            )
            return str(err)
