import json

from django.conf import settings
from decimal import Decimal

import stripe
from keel.Core.err_log import logging_format
from keel.Core.constants import LOGGER_CRITICAL_SEVERITY

import logging
logger = logging.getLogger('app-logger')

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe_webhook_event_signing_secret = settings.STRIPE_WEBHOOK_SIGNING_SECRET


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

    def __init__(self, payment_manager):
        self._payment_manager = payment_manager

    def process_event(self):
        raise NotImplementedError


class PaymentIntentEventHandler(IPaymentEventHandler):

    def __init__(self, payment_manager, event_data):
        super().__init__(payment_manager)
        self._payment_intent_id = event_data.id

    def process_event(self):
        self._payment_manager.complete_payment_transaction(self._payment_intent_id)


class PaymentEventManager:
    eventHandlers = {
        "payment_intent.succeeded": PaymentIntentEventHandler,
        # "charge.succeeded":
    }

    def process(self, payment_manager, webhook_payload, signature):
        try:
            event = stripe.Webhook.construct_event(
                webhook_payload, signature, stripe_webhook_event_signing_secret
            )
        except ValueError as err:
            err_msg = "Invalid stripe payload - {} with error - {}".format(webhook_payload, err)
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "", description=err_msg))
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as err:
            err_msg = "Inavlid stripe signature - {} with error - {}".format(signature, err)
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "", description=err_msg))
            raise ValueError("Invalid signature")

        handler = self.eventHandlers.get(event.type)
        if handler:
            handler_obj = handler(payment_manager, event.data.object)
            try:
                handler_obj.process_event()
            except Exception as err:
                err_msg = "Error while processing event - {} with error - {}".format(event, err)
                logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "",
                                            description=err_msg))
                raise ValueError("Error while handling the event")
        else:
            err_msg = "Handler not implemented for event type - {} & event - {}".format(event.type, event)
            logger.error(logging_format(LOGGER_CRITICAL_SEVERITY, "PaymentEventManager.process_event", "",
                                        description=err_msg))
            # raise NotImplementedError("Event is not handled - {}".format(event))


STRIPE_PAYMENT_OBJECT = StripePaymentUtility()
STRIPE_EVENT_MANAGER = PaymentEventManager()
