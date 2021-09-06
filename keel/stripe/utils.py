from django.conf import settings
from decimal import Decimal

import stripe
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY

import logging
logger = logging.getLogger('app-logger')

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentUtility(object):

    def validate_amount(self, amount):
        try:
            amount = Decimal(amount)
        except ValueError as err:
            err_msg = "Invalid Amount"
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "StripePaymentUtility.validate_amount", "", description=err_msg))
            raise ValueError(err_msg)

    def create_new_payment(self, amount, currency="usd"):
        self.validate_amount(amount)
        # stripe_currency = CurrencyMapping.objects.get(user_currency=currency)
        stripe_currency = currency
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency=stripe_currency
            )
            return {
                "status": 1,
                "error": "",
                "data": {
                    "unique_identifier": intent["id"],
                    "client_secret": intent["client_secret"]
                }
            }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "data": {}
            }


class IPaymentEventHandler(object):

    def __init__(self, transaction_identifier):
        self.transaction_identifier = transaction_identifier

    def process_event(self):
        from keel.payment.implementation.pay_manager import PaymentManager
        payment_manager = PaymentManager()
        payment_manager.complete_payment_transaction(self.transaction_identifier)


class PaymentIntentEventHandler(IPaymentEventHandler):

    def __init__(self, intent_id):
        super().__init__(intent_id)


class PaymentEventManager:
    eventHandlers = {
        "payment_intent.succeeded": PaymentIntentEventHandler
    }

    def process(self, webhook_payload):
        try:
            event = stripe.Event.construct_from(
                webhook_payload, stripe.api_key
            )
            handler = self.eventHandlers.get(event.type)
            if handler:
                handler_obj = handler(event.data.object)
                handler_obj.process_event()
            else:
                err_msg = ""
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "",
                                            description=err_msg))
                raise NotImplementedError("Event is not handled - {}".format(event))
        except ValueError as e:
            err_msg = ""
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "", description=err_msg))
            raise ValueError("")


STRIPE_PAYMENT_OBJECT = StripePaymentUtility()
STRIPE_EVENT_MANAGER = PaymentEventManager()
