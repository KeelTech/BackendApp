from django.conf import settings
from django.db import models, transaction
from datetime import date, datetime, timedelta
from safedelete import SOFT_DELETE
from safedelete.models import SafeDeleteModel

import requests
import json
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class User(AbstractBaseUser, PermissionsMixin):
    STAFF = 1
    DOCTOR = 2
    CONSUMER = 3
    USER_TYPE_CHOICES = ((STAFF, 'staff'), (DOCTOR, 'doctor'), (CONSUMER, 'user'))
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    # EMAIL_FIELD = 'email'
    objects = CustomUserManager()
    username = None
    first_name = None
    phone_number = models.CharField(max_length=10, blank=False, null=True, default=None)
    email = models.EmailField(max_length=100, blank=False, null=True, default=None)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    is_phone_number_verified = models.BooleanField(verbose_name= 'Phone Number Verified', default=False)
    is_active = models.BooleanField(verbose_name= 'Active', default=True, help_text= 'Designates whether this user should be treated as active.')

    is_staff = models.BooleanField(verbose_name= 'Staff Status', default=False, help_text= 'Designates whether the user can log into this admin site.')
    date_joined = models.DateTimeField(auto_now_add=True)
    auto_created = models.BooleanField(default=False)
    source = models.CharField(blank=True, max_length=50, null=True)
    data = JSONField(blank=True, null=True)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if self and other and self.id and other.id:
            return self.id == other.id
        return False

    def __str__(self):
        name = self.phone_number
        try:
            name = self.staffprofile.name
        except:
            pass
        return name
        # if self.user_type==1 and hasattr(self, 'staffprofile'):
        #     return self.staffprofile.name
        # return str(self.phone_number)

    @cached_property
    def active_plus_user(self):
        active_plus_user = self.active_plus_users.filter().order_by('-id').first()
        return active_plus_user if active_plus_user and active_plus_user.is_valid() else None

    @cached_property
    def get_temp_plus_user(self):
        from keel.plus.models import TempPlusUser
        temp_plus_user = TempPlusUser.objects.filter(user_id=self.id, deleted=0).order_by('-id').first()
        return temp_plus_user if temp_plus_user else None

    @cached_property
    def inactive_plus_user(self):
        from keel.plus.models import PlusUser
        inactive_plus_user = PlusUser.objects.filter(status=PlusUser.INACTIVE, user_id=self.id).order_by('-id').first()
        return inactive_plus_user if inactive_plus_user else None

    @classmethod
    def get_external_login_data(cls, data, request=None):
        from keel.authentication.backends import JWTAuthentication
        profile_data = {}
        source = data.get('extra').get('utm_source', 'External') if data.get('extra') else 'External'
        redirect_type = data.get('redirect_type', "")

        user = User.objects.filter(phone_number=data.get('phone_number'),
                                                     user_type=User.CONSUMER).first()
        user_with_email = User.objects.filter(email=data.get('email', None), user_type=User.CONSUMER).first()
        if not user and user_with_email:
            raise Exception("Email already taken with another number")
        if not user:
            user = User.objects.create(phone_number=data.get('phone_number'),
                                       is_phone_number_verified=False,
                                       user_type=User.CONSUMER,
                                       auto_created=True,
                                       email=data.get('email'),
                                       source=source,
                                       data=data.get('extra'))

        if not user:
            raise Exception('Invalid User')
            # return JsonResponse(response, status=400)

        profile_data['name'] = data.get('name')
        profile_data['phone_number'] = user.phone_number
        profile_data['user'] = user
        profile_data['email'] = data.get('email')
        profile_data['source'] = source
        profile_data['dob'] = data.get('dob', None)
        profile_data['gender'] = data.get('gender', None)
        user_profiles = user.profiles.all()

        if not bool(re.match(r"^[a-zA-Z ]+$", data.get('name'))):
            raise Exception('Invalid Name')
            # return Response({"error": "Invalid Name"}, status=status.HTTP_400_BAD_REQUEST)

        if user_profiles:
            user_profiles = list(filter(lambda x: x.name.lower() == profile_data['name'].lower(), user_profiles))
            if user_profiles:
                user_profile = user_profiles[0]
                if not user_profile.phone_number:
                    user_profile.phone_number = profile_data['phone_number']
                if not user_profile.email:
                    user_profile.email = profile_data['email'] if not user_profile.email else None
                if not user_profile.gender and profile_data.get('gender', None):
                    user_profile.gender = profile_data.get('gender', None)
                if not user_profile.dob and profile_data.get('dob', None):
                    user_profile.dob = profile_data.get('dob', None)
                user_profile.save()
            else:
                UserProfile.objects.create(**profile_data)
        else:
            profile_data.update({
                "is_default_user": True
            })
            profile_data.pop('doctor', None)
            profile_data.pop('hospital', None)
            UserProfile.objects.create(**profile_data)

        token_object = JWTAuthentication.generate_token(user, request)
        result = dict()
        result['token'] = token_object
        result['user_id'] = user.id
        return result


    def is_valid_lead(self, date_time_to_be_checked, check_lab_appointment=False, check_ipd_lead=False):
        # If this user has booked an appointment with specific period from date_time_to_be_checked, then
        # the lead is valid else invalid.
        from keel.doctor.models import OpdAppointment
        from keel.diagnostic.models import LabAppointment
        from keel.procedure.models import IpdProcedureLead
        any_appointments = OpdAppointment.objects.filter(user=self, created_at__gte=date_time_to_be_checked,
                                                         created_at__lte=date_time_to_be_checked + timezone.timedelta(
                                                             minutes=settings.LEAD_AND_APPOINTMENT_BUFFER_TIME)).exists()
        if check_lab_appointment and not any_appointments:
            any_appointments = LabAppointment.objects.filter(user=self, created_at__gte=date_time_to_be_checked,
                                                             created_at__lte=date_time_to_be_checked + timezone.timedelta(
                                                                 minutes=settings.LEAD_AND_APPOINTMENT_BUFFER_TIME)).exists()
        if check_ipd_lead and not any_appointments:
            count = IpdProcedureLead.objects.filter(user=self, is_valid=True,
                                                    created_at__lte=date_time_to_be_checked,
                                                    created_at__gte=date_time_to_be_checked - timezone.timedelta(
                                                        minutes=settings.LEAD_AND_APPOINTMENT_BUFFER_TIME)).count()
            if count > 0:
                any_appointments = True
        return not any_appointments

    @cached_property
    def show_ipd_popup(self):
        from keel.procedure.models import IpdProcedureLead
        lead = IpdProcedureLead.objects.filter(phone_number=self.phone_number,
                                               created_at__gt=timezone.now() - timezone.timedelta(hours=1)).first()
        if lead:
            return False
        return True

    @cached_property
    def force_ipd_popup(self):
        from keel.procedure.models import IpdProcedureLead
        lead = IpdProcedureLead.objects.filter(phone_number=self.phone_number).exists()
        if lead:
            return False
        return True

    @cached_property
    def active_insurance(self):
        active_insurance = self.purchased_insurance.filter().order_by('id').last()
        return active_insurance if active_insurance and active_insurance.is_valid() else None

    @cached_property
    def onhold_insurance(self):
        from keel.insurance.models import UserInsurance
        onhold_insurance = self.purchased_insurance.filter(status=UserInsurance.ONHOLD).order_by('-id').first()
        return onhold_insurance if onhold_insurance else None

    @cached_property
    def recent_opd_appointment(self):
        return self.appointments.filter(created_at__gt=timezone.now() - timezone.timedelta(days=90)).order_by('-id')

    @cached_property
    def recent_lab_appointment(self):
        return self.lab_appointments.filter(created_at__gt=timezone.now() - timezone.timedelta(days=90)).order_by('-id')

    def get_phone_number_for_communication(self):
        from keel.communications.models import unique_phone_numbers
        receivers = []
        default_user_profile = self.profiles.filter(is_default_user=True).first()
        if default_user_profile and default_user_profile.phone_number:
            receivers.append({'user': self, 'phone_number': default_user_profile.phone_number})
        receivers.append({'user': self, 'phone_number': self.phone_number})
        receivers = unique_phone_numbers(receivers)
        return receivers

    def get_full_name(self):
        return self.full_name

    @cached_property
    def full_name(self):
        profile = self.get_default_profile()
        if profile and profile.name:
            return profile.name
        return ''

    @cached_property
    def get_default_email(self):
        profile = self.get_default_profile()
        if profile and profile.email:
            return profile.email
        return ''

    @property
    def username(self):
        if self.email:
            return self.email
        return ''

    # @cached_property
    # def get_default_profile(self):
    #     user_profile = self.profiles.all().filter(is_default_user=True).first()
    #     if user_profile:
    #         return user_profile
    #     return ''
        
        # self.profiles.filter(is_default=True).first()

    @cached_property
    def my_groups(self):
        return self.groups.all()

    def is_member_of(self, group_name):
        for group in self.my_groups:
            if group.name == group_name:
                return True

        return False

    def get_unrated_opd_appointment(self):
        from keel.doctor import models as doc_models
        opd_app = None
        opd_all = self.appointments.all().order_by('-id')
        for opd in opd_all:
            if opd.status == doc_models.OpdAppointment.COMPLETED:
                if opd.is_rated == False and opd.rating_declined == False:
                    opd_app = opd
                break
        return opd_app

    def get_unrated_lab_appointment(self):
        from keel.diagnostic import models as lab_models
        lab_app = None
        lab_all = self.lab_appointments.all().order_by('-id')
        for lab in lab_all:
            if lab.status == lab_models.LabAppointment.COMPLETED:
                if lab.is_rated == False and lab.rating_declined == False:
                    lab_app = lab
                break
        return lab_app

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        return super().save(*args, **kwargs)

    def get_default_profile(self):
        default_profile = self.profiles.filter(is_default_user=True)
        if default_profile.exists():
            return default_profile.first()
        else:
            return None

    class Meta:
        unique_together = (("email", "user_type"), ("phone_number","user_type"))
        db_table = "auth_user"


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    def mark_delete(self):
        self.deleted_at = datetime.now()
        self.save()

    class Meta:
        abstract = True


class CreatedByModel(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    MALE = 'm'
    FEMALE = 'f'
    OTHER = 'o'
    GENDER_CHOICES = [(MALE,"Male"), (FEMALE,"Female"), (OTHER,"Other")]
    user = models.ForeignKey(User, related_name="profiles", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, blank=False, null=True, default=None)
    email = models.CharField(max_length=256, blank=False, null=True, default=None)
    gender = models.CharField(max_length=2, default=None, blank=True, null=True, choices=GENDER_CHOICES)
    phone_number = models.BigIntegerField(blank=True, null=True, validators=[MaxValueValidator(9999999999), MinValueValidator(1000000000)])
    is_otp_verified = models.BooleanField(default=False)
    is_default_user = models.BooleanField(default=False)
    dob = models.DateField(blank=True, null=True)
    source = models.CharField(blank=True, max_length=50, null=True)
    
    profile_image = models.ImageField(upload_to='users/images', height_field=None, width_field=None, blank=True, null=True)
    whatsapp_optin = models.NullBooleanField(default=None) # optin check of the whatsapp
    whatsapp_is_declined = models.BooleanField(default=False)  # flag to whether show whatsapp pop up or not.

    def __str__(self):
        return "{}-{}".format(self.name, self.id)

    @cached_property
    def is_insured_profile(self):
        insured_member_profile = self.insurance.filter().order_by('-id').first()
        response = True if insured_member_profile and insured_member_profile.user_insurance.is_valid() else False
        return response

    def get_thumbnail(self):
        if self.profile_image:
            return self.profile_image.url
        return None
        # return static('doctor_images/no_image.png')

    @cached_property
    def get_plus_membership(self):
        plus_member = self.plus_member.all().order_by('-id').first()
        if plus_member:
            return plus_member.plus_user if plus_member.plus_user.is_valid() else None

        return None

    def verify_profile(self):
        if self.dob and self.name:
            return True
        else:
            return False

    @cached_property
    def get_temp_plus_membership(self):
        from keel.plus.models import TempPlusUser
        plus_user = TempPlusUser.objects.filter(profile_id=self.id, deleted=0).first()
        return plus_user

    def has_image_changed(self):
        if not self.pk:
            return True
        old_value = self.__class__._default_manager.filter(pk=self.pk).values('profile_image').get()['profile_image']
        return not getattr(self, 'profile_image').name == old_value

    def get_age(self):
        user_age = None
        if self.dob:
            today = date.today()
            user_age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return user_age

    @cached_property
    def is_gold_profile(self):
        plus_member_profile = self.plus_member.filter().order_by('-id').first()
        response = True if plus_member_profile and plus_member_profile.plus_user.is_valid() else False
        return response

    def save(self, *args, **kwargs):
        if not self.has_image_changed():
            return super().save(*args, **kwargs)

        if self.profile_image:
            max_allowed = 1000
            img = Img.open(self.profile_image)
            size = img.size
            if max(size)>max_allowed:
                size = tuple(math.floor(ti/(max(size)/max_allowed)) for ti in size)

            img = img.resize(size, Img.ANTIALIAS)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            md5_hash = hashlib.md5(img.tobytes()).hexdigest()
            new_image_io = BytesIO()
            img.save(new_image_io, format='JPEG')
            self.profile_image = InMemoryUploadedFile(new_image_io, None, md5_hash + ".jpg", 'image/jpeg',
                                                      new_image_io.tell(), None)
        super().save(*args, **kwargs)

    def update_profile_post_endorsement(self, endorsed_data):
        self.name = endorsed_data.first_name + " " + endorsed_data.middle_name + " " + endorsed_data.last_name
        self.email = endorsed_data.email
        if endorsed_data.gender == 'f':
            self.gender = UserProfile.FEMALE
        elif endorsed_data.gender == 'm':
            self.gender = UserProfile.MALE
        else:
            self.gender = UserProfile.OTHER
        if endorsed_data.phone_number:
            self.phone_number = endorsed_data.phone_number
        else:
            self.phone_number = self.user.phone_number
        self.dob = endorsed_data.dob
        self.save()

    def is_insurance_package_limit_exceed(self):
        from keel.diagnostic.models import LabAppointment
        from keel.doctor.models import OpdAppointment
        user = self.user
        insurance = None
        if user.is_authenticated:
            insurance = user.active_insurance
        if not insurance or not self.is_insured_profile:
            return False
        package_count = 0
        previous_insured_lab_bookings = LabAppointment.objects.prefetch_related('tests').filter(insurance=insurance, profile=self).exclude(status=OpdAppointment.CANCELLED)
        for booking in previous_insured_lab_bookings:
            all_tests = booking.tests.all()
            for test in all_tests:
                if test.is_package:
                    package_count += 1

        if package_count >= insurance.insurance_plan.plan_usages.get('member_package_limit'):
            return True
        else:
            return False


    class Meta:
        db_table = "user_profile"

