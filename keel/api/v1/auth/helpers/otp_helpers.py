from keel.authentication.models import SMSOtpModel
from keel.Core.helpers import generate_random_int
from django.utils import timezone
from datetime import timedelta


class OTPHelper(object):
    def __init__(self, user, phone_number):
        self.phone_number = phone_number
        self.user = user

    def generate_otp(self):
        otp = generate_random_int(4)
        self.otp = otp
        return otp

    def save_otp(self):
        self.generate_otp()
        expiry_time = timezone.now() + timedelta(minutes=10)

        # try:
        otp_model = SMSOtpModel(
            phone_number=self.phone_number,
            otp=self.otp,
            user=self.user,
            otp_expiry=expiry_time,
            otp_status = True
        )
        otp_model.save()
        # except Exception as e:
        #     print(e)
        #     pass
        return otp_model.otp

    def delete_otp(self):
        otp_model = SMSOtpModel.objects.filter(phone_number=self.phone_number)
        otp_model.delete()
        return True
