import uuid

import requests
from django.conf import settings
from keel.Core.constants import LOGGER_LOW_SEVERITY, LOGGER_LOG_MESSAGE
from keel.Core.err_log import log_error
from keel.payment.models import RazorPayTransactions
from requests.auth import HTTPBasicAuth

RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET


class RazorPay(object):
    def __init__(self, amount, currency, **kwargs):
        self.amount = amount
        self.currency = currency

    def create_order(self):
        amount_in_paise = self.amount * 100

        url = "https://api.razorpay.com/v1/orders"

        payload = {
            "amount": amount_in_paise,
            "currency": self.currency,
        }
        resp = {}
        try:
            response = requests.request(
                "POST",
                url,
                data=payload,
                auth=HTTPBasicAuth(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            )
            response_json = response.json()
            resp["id"] = response_json.get("id")
            log_error(
                LOGGER_LOG_MESSAGE,
                "RazorPay: create_order::success",
                "",
                description=str(response_json),
            )

        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "RazorPay: create_order",
                "",
                description=str(err),
            )
            resp["error"] = str(err)
        return resp

    def capture_payment(self, payment_id):
        amount = self.amount * 1000

        url = f"https://api.razorpay.com/v1/payments/{payment_id}/capture"

        payload = {"amount": amount, "currency": self.currency}

        try:
            response = requests.request(
                "POST",
                url,
                data=payload,
                auth=HTTPBasicAuth(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            )
        except Exception as err:
            log_error(
                LOGGER_LOW_SEVERITY,
                "RazorPay:capture_payment",
                "",
                description=str(err),
            )
            return str(err)

        return response.json()


def generate_transaction_id():

    # check if the transaction id is already in the database
    # and recursively generate a new one

    while True:
        transaction_id = uuid.uuid4()
        if not RazorPayTransactions.objects.filter(
            transaction_id=transaction_id
        ).exists():
            return transaction_id
