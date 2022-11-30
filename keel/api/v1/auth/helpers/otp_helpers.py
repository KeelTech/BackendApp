from datetime import timedelta

from django.utils import timezone
from keel.authentication.models import SMSOtpModel
from keel.Core.err_log import log_error
from keel.Core.helpers import generate_random_int


class OTPHelper(object):
    def __init__(self, phone_number):
        self.phone = phone_number
        self.otp = None

    def generate_otp(self):
        otp = generate_random_int(4)
        self.otp = otp
        return otp

    def save_otp(self, phone_number):
        self.generate_otp()
        expiry_time = timezone.now() + timedelta(minutes=10)

        try:
            otp_model = SMSOtpModel(
                phone_number=phone_number,
                otp=self.otp,
                user=None,
                otp_expiry=expiry_time,
                otp_status=True,
            )
            otp_model.save()
        except Exception as e:
            log_error(
                "ERORR",
                "CommentService: post postComments",
                str(self.phone),
                err=str(e),
            )
            pass

        return otp_model.otp

    def verify_otp(self, otp):
        otp_model = SMSOtpModel.objects.filter(phone_number=self.phone, otp=otp, otp_status=True).first()
        if otp_model:
            otp_model.otp_status = False
            otp_model.save()
            data = {"otp": otp_model.otp, "phone_number": otp_model.phone_number}
            return data
        else:
            return False

    def delete_otp(self):
        otp_model = SMSOtpModel.objects.filter(phone_number=self.phone)
        otp_model.delete()
        return True
