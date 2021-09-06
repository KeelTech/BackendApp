from abc import ABC


class I3PPaymentService(ABC):
    def __init__(self):
        pass

    def get_pay_details(self, amount):
        raise NotImplementedError

    def refund_pay(self, amount, **kwargs):
        raise NotImplementedError

    def cancel_pay(self, transaction_details, **kwargs):
        raise NotImplementedError
