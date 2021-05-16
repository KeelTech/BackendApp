from urllib.parse import urlparse

from django.core.files.uploadedfile import TemporaryUploadedFile, UploadedFile
from rest_framework.views import exception_handler
from rest_framework import permissions, status
from collections import defaultdict
from operator import itemgetter
from itertools import groupby
from django.db import connection, transaction, connections
from django.db.models import F, Func, Q, Count, Sum, Case, When, Value, IntegerField
from django.utils import timezone
import math
import pytz
import calendar
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from keel.account.tasks import refund_curl_task
from keel.coupon.models import UserSpecificCoupon
from keel.crm.constants import constants
import copy
import requests
import json
import random
import string
import uuid
from django.conf import settings
from dateutil.parser import parse
from dateutil import tz
from decimal import Decimal
from collections import OrderedDict
import datetime
from django.utils.dateparse import parse_datetime
import hashlib
from keel.authentication import models as auth_models
import logging
from datetime import timedelta
import os
import tempfile

import base64, hashlib
from Crypto import Random
from Crypto.Cipher import AES
import decimal


logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTemporaryUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """
    def __init__(self, name, content_type, size, charset, prefix, suffix, content_type_extra=None):
        _, ext = os.path.splitext(name)
        file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, dir=settings.FILE_UPLOAD_TEMP_DIR)
        super().__init__(file, name, content_type, size, charset, content_type_extra)

    def temporary_file_path(self):
        """Return the full path of this file."""
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except FileNotFoundError:
            # The file was moved or deleted before the tempfile could unlink
            # it. Still sets self.file.close_called and calls
            # self.file.file.close() before the exception.
            pass


def get_pdf_njs(html, filename):
    params = {'html': html, 'filename': filename}
    odbc_base_url = str(settings.ODBC_BASE_URL)
    url = odbc_base_url + '/api/get_pdf'
    # url = 'http://localhost:8000/api/get_pdf'
    response = requests.post(url, data=params, stream=True)
    if response.status_code == 200:
        object = response
        return object
    logger.error("Error Generating PDF " + str(filename) + " from PDF Server " + str(response.text))
    return None

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield subkey, subvalue
            else:
                yield key, value

    return dict(items())


def first_error_only(d):
    code_mapping = {'min_value':'invalid', 'max_value':'invalid','invalid_choice':'invalid', 'null':'required'}

    new_dict = {}
    for key, value in d.items():
        if isinstance(value, (list,)) and value:
            new_dict[key] = value[0]
            new_dict[key]['code'] = code_mapping.get(new_dict[key]['code'],new_dict[key]['code'])

    return new_dict


def formatted_errors(dic):
    return first_error_only(flatten_dict(dic))


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        try:
            data = formatted_errors(exc.get_full_details())
            nfe = data.get('non_field_errors')
            if nfe:
                del data['non_field_errors']
                data['request_errors'] = nfe

            response.data = data
        except Exception:
            pass

    return response


def group_consecutive_numbers(data):
    ranges = []
    for k, g in groupby(enumerate(data), lambda x: x[0] - x[1]):
        group = list(map(itemgetter(1), g))
        ranges.append((group[0], group[-1]))
    return ranges


def convert_timings(timings, is_day_human_readable=True):
    from keel.doctor.models import DoctorClinicTiming
    if not is_day_human_readable:
        DAY_MAPPING = {value[0]: (value[0], value[1][:3]) for value in DoctorClinicTiming.DAY_CHOICES}
    else:
        DAY_MAPPING = {value[1]: (value[0], value[1][:3]) for value in DoctorClinicTiming.DAY_CHOICES}
    DAY_MAPPING_REVERSE = {value[0]: value[1][:3] for value in DoctorClinicTiming.DAY_CHOICES}
    TIMESLOT_MAPPING = {value[0]: value[1] for value in DoctorClinicTiming.TIME_CHOICES}
    temp = defaultdict(list)
    for timing in timings:
        temp[(float(timing.get('start')), float(timing.get('end')))].append(DAY_MAPPING.get(timing.get('day')))
    for key, value in temp.items():
        temp[key] = sorted(value, key=itemgetter(0))
    final_dict = defaultdict(list)
    keys_list = list(TIMESLOT_MAPPING.keys())
    for key, value in temp.items():
        grouped_consecutive_days = group_consecutive_numbers(map(lambda x: x[0], value))
        response_keys = []
        for days in grouped_consecutive_days:
            if days[0] == days[1]:
                response_keys.append(DAY_MAPPING_REVERSE.get(days[0]))
            else:
                response_keys.append("{}-{}".format(DAY_MAPPING_REVERSE.get(days[0]),
                                                    DAY_MAPPING_REVERSE.get(days[1])))
        start_time = TIMESLOT_MAPPING.get(key[0])
        end_time = TIMESLOT_MAPPING.get(key[1])
        if not start_time and key[0] < keys_list[0]:
            start_time = TIMESLOT_MAPPING.get(keys_list[0])
        if not end_time and key[1] > keys_list[-1]:
            end_time = TIMESLOT_MAPPING.get(keys_list[-1])
        if not key[0] > key[1]:
            if start_time and end_time:
                final_dict[",".join(response_keys)].append("{} to {}".format(start_time, end_time))
            else:
                final_dict[",".join(response_keys)].append("")
    return final_dict


def clinic_convert_timings(timings, is_day_human_readable=True):
    from keel.doctor.models import DoctorClinicTiming
    if not is_day_human_readable:
        DAY_MAPPING = {value[0]: (value[0], value[1][:3]) for value in DoctorClinicTiming.DAY_CHOICES}
    else:
        DAY_MAPPING = {value[1]: (value[0], value[1][:3]) for value in DoctorClinicTiming.DAY_CHOICES}
    DAY_MAPPING_REVERSE = {value[0]: value[1][:3] for value in DoctorClinicTiming.DAY_CHOICES}
    TIMESLOT_MAPPING = {value[0]: value[1] for value in DoctorClinicTiming.TIME_CHOICES}
    temp = defaultdict(list)
    for timing in timings:
        temp[(timing.start, timing.end)].append(DAY_MAPPING.get(timing.day))
    for key, value in temp.items():
        temp[key] = sorted(value, key=itemgetter(0))
    final_dict = defaultdict(list)
    for key, value in temp.items():
        grouped_consecutive_days = group_consecutive_numbers(map(lambda x: x[0], value))
        response_keys = []
        for days in grouped_consecutive_days:
            if days[0] == days[1]:
                response_keys.append(DAY_MAPPING_REVERSE.get(days[0]))
            else:
                response_keys.append("{}-{}".format(DAY_MAPPING_REVERSE.get(days[0]),
                                                    DAY_MAPPING_REVERSE.get(days[1])))
        final_dict[",".join(response_keys)].append("{} to {}".format(TIMESLOT_MAPPING.get(key[0]),
                                                                     TIMESLOT_MAPPING.get(key[1])))
    return final_dict

class RawSql:
    def __init__(self, query, parameters, db='default'):
        self.query = query
        self.parameters = parameters
        self.db = db

    def fetch_all(self):
        result = []
        try:
            with connections[self.db].cursor() as cursor:
                cursor.execute(self.query, self.parameters)
                columns = [col[0] for col in cursor.description]
                result = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(e)
            print('Failed to connect to slave db')
        return result

    def execute(self):
        try:
            with connections[self.db].cursor() as cursor:
                cursor.execute(self.query, self.parameters)
        except Exception as e:
            print(e)
            print('Failed to connect to slave db')


class AgreedPriceCalculate(Func):
    function = 'labtest_agreed_price_calculate'


class DealPriceCalculate(Func):
    function = 'labtest_deal_price_calculate'


def form_time_slot(timestamp, time):
    to_zone = tz.gettz(settings.TIME_ZONE)
    min, hour = math.modf(time)
    min *= 60
    dt_field = timestamp.astimezone(to_zone).replace(hour=int(hour), minute=int(min), second=0, microsecond=0)
    return dt_field


def get_previous_month_year(month, year):
    dt = "01" + str(month) + str(year)
    dt = datetime.datetime.strptime(dt, "%d%m%Y")
    prev_dt = dt - datetime.timedelta(days=1)
    return prev_dt.month, prev_dt.year


def get_start_end_datetime(month, year, local_dt=None):
    now = timezone.now()
    if local_dt is not None:
        local_dt = timezone.localtime(now)
    else:
        dt = "01" + str(month) + str(year)
        dt = datetime.datetime.strptime(dt, "%d%m%Y")
        local_timezone = timezone.get_default_timezone().__str__()
        dt = pytz.timezone(local_timezone).localize(dt)
        local_dt = timezone.localtime(dt)
    start_dt = local_dt.replace(hour=0, minute=0, second=0, microsecond=0, day=1)
    end_dt = get_last_date_time(local_dt)
    return start_dt, end_dt


def get_last_date_time(dt):
    t, last_date = calendar.monthrange(dt.year, dt.month)
    return dt.replace(hour=23, minute=59, second=59, microsecond=0, day=last_date)


class IsConsumer(permissions.BasePermission):
    message = 'Consumer is allowed to perform action only.'

    def has_permission(self, request, view):
        if request.user.user_type == User.CONSUMER:
            return True
        return False


class IsDoctor(permissions.BasePermission):
    message = 'Doctor is allowed to perform action only.'

    def has_permission(self, request, view):
        if request.user.user_type == User.DOCTOR:
            return True
        return False


class IsNotAgent(permissions.BasePermission):
    message = 'Agent is not allowed to perform this action.'

    def has_permission(self, request, view):
        if hasattr(request, 'agent') and request.agent is not None:
            return False
        return True


class IsMatrixUser(permissions.BasePermission):
    message = 'Only Matrix User is allowed to Perform Action.'

    def has_permission(self, request, view):
        token = request.META.get('HTTP_MATRIX_AUTHORIZATION', None)
        if token is not None:
            if token == settings.MATRIX_AUTH_TOKEN:
                return True
        return False


def plus_subscription_transform(app_data):
    """A serializer helper to serialize Insurance data"""

    app_data['plus_user']['purchase_date'] = str(
        app_data['plus_user']['purchase_date'])
    app_data['plus_user']['expire_date'] = str(
        app_data['plus_user']['expire_date'])

    app_data['profile_detail']['dob'] = str(app_data['profile_detail']['dob'])
    insured_members = app_data['plus_user']['plus_members']
    for member in insured_members:
        member['dob'] = str(member['dob'])
        # member['member_profile']['dob'] = str(member['member_profile']['dob'])
    return app_data


def plan_subscription_reverse_transform(subscription_data):
    subscription_data['plus_user']['purchase_date'] = \
        datetime.datetime.strptime(subscription_data['plus_user']['purchase_date'], "%Y-%m-%d %H:%M:%S.%f")
    subscription_data['plus_user']['expire_date'] = \
        datetime.datetime.strptime(subscription_data['plus_user']['expire_date'],
                                   "%Y-%m-%d %H:%M:%S.%f")
    subscription_data['profile_detail']['dob'] = \
        datetime.datetime.strptime(subscription_data['profile_detail']['dob'],
                                   "%Y-%m-%d")
    plus_members = subscription_data['plus_user']['plus_members']
    for member in plus_members:
        member['dob'] = datetime.datetime.strptime(str(member['dob']), "%Y-%m-%d").date()
    return subscription_data


def insurance_transform(app_data):
    """A serializer helper to serialize Insurance data"""
    # app_data['insurance']['insurance_transaction']['transaction_date'] = str(app_data['insurance']['insurance_transaction']['transaction_date'])
    # app_data['insurance']['profile_detail']['dob'] = str(app_data['insurance']['profile_detail']['dob'])
    # insured_members = app_data['insurance']['insurance_transaction']['insured_members']
    # for member in insured_members:
    #     member['dob'] = str(member['dob'])
    #     # member['member_profile']['dob'] = str(member['member_profile']['dob'])
    # return app_data
    app_data['user_insurance']['purchase_date'] = str(
        app_data['user_insurance']['purchase_date'])
    app_data['user_insurance']['expiry_date'] = str(
        app_data['user_insurance']['expiry_date'])
    app_data['profile_detail']['dob'] = str(app_data['profile_detail']['dob'])
    insured_members = app_data['user_insurance']['insured_members']
    for member in insured_members:
        member['dob'] = str(member['dob'])
        # member['member_profile']['dob'] = str(member['member_profile']['dob'])
    return app_data


def insurance_reverse_transform(insurance_data):
    insurance_data['user_insurance']['purchase_date'] = \
        datetime.datetime.strptime(insurance_data['user_insurance']['purchase_date'], "%Y-%m-%d %H:%M:%S.%f")
    insurance_data['user_insurance']['expiry_date'] = \
        datetime.datetime.strptime(insurance_data['user_insurance']['expiry_date'],
                                   "%Y-%m-%d %H:%M:%S.%f")
    insurance_data['profile_detail']['dob'] = \
        datetime.datetime.strptime(insurance_data['profile_detail']['dob'],
                                   "%Y-%m-%d")
    insured_members = insurance_data['user_insurance']['insured_members']
    for member in insured_members:
        member['dob'] = datetime.datetime.strptime(member['dob'], "%Y-%m-%d").date()
    return insurance_data


def opdappointment_transform(app_data):
    """A serializer helper to serialize OpdAppointment data"""
    app_data["deal_price"] = str(app_data["deal_price"])
    app_data["fees"] = str(app_data["fees"])
    app_data["effective_price"] = str(app_data["effective_price"])
    app_data["mrp"] = str(app_data["mrp"])
    app_data["discount"] = str(app_data["discount"])
    app_data["time_slot_start"] = str(app_data["time_slot_start"])
    app_data["doctor"] = app_data["doctor"].id
    app_data["hospital"] = app_data["hospital"].id
    app_data["profile"] = app_data["profile"].id
    app_data["user"] = app_data["user"].id
    app_data["booked_by"] = app_data["booked_by"].id
    app_data["_responsible_user"] = app_data.get("_responsible_user", None)
    app_data["_source"] = app_data.get("_source", None)
    if app_data.get("coupon"):
        app_data["coupon"] = list(app_data["coupon"])
    return app_data


def labappointment_transform(app_data):
    app_data["price"] = str(app_data["price"])
    app_data["agreed_price"] = str(app_data["agreed_price"])
    app_data["deal_price"] = str(app_data["deal_price"])
    app_data["effective_price"] = str(app_data["effective_price"])
    app_data["discount"] = str(app_data["discount"])
    app_data["time_slot_start"] = str(app_data["time_slot_start"])
    app_data["lab"] = app_data["lab"].id
    app_data["user"] = app_data["user"].id
    app_data["profile"] = app_data["profile"].id
    app_data["home_pickup_charges"] = str(app_data.get("home_pickup_charges",0))
    prescription_objects = app_data.get("prescription_list", [])
    test_time_slots = app_data.get('test_time_slots', [])
    if prescription_objects:
        prescription_id_list = []
        for prescription_data in prescription_objects:
            prescription_id_list.append({'prescription': prescription_data.get('prescription').id})
        app_data["prescription_list"] = prescription_id_list

    if test_time_slots:
        for test_time_slot in test_time_slots:
            test_time_slot['time_slot_start'] = str(test_time_slot['time_slot_start'])
        app_data['test_time_slots'] = test_time_slots

    if app_data.get("coupon"):
        app_data["coupon"] = list(app_data["coupon"])
    if app_data.get("user_plan"):
        app_data["user_plan"] = app_data["user_plan"].id
    app_data["_responsible_user"] = app_data.get("_responsible_user", None)
    app_data["_source"] = app_data.get("_source", None)
    return app_data


def refund_curl_request(req_data):
    for data in req_data:
        refund_curl_task.apply_async((data, ), countdown=1)
        # refund_curl_task.delay(data)


def custom_form_datetime(time_str, to_zone, diff_days=0):
    next_dt = timezone.now().replace(tzinfo=to_zone).date()
    if diff_days:
        next_dt += datetime.timedelta(days=diff_days)
    exp_dt = str(next_dt) + " " + time_str
    exp_dt = parse(exp_dt).replace(tzinfo=to_zone)

    return exp_dt

class ErrorCodeMapping(object):
    IVALID_APPOINTMENT_ORDER = 1


def is_valid_testing_data(user, doctor):

    if doctor.is_test_doctor and not user.groups.filter(name=constants['TEST_USER_GROUP']).exists():
        return False
    return True


def is_valid_testing_lab_data(user, lab):

    if lab.is_test_lab and not user.groups.filter(name=constants['TEST_USER_GROUP']).exists():
        return False
    return True


def single_booking_payment_details(request, orders):
    from keel.account.models import PgTransaction, Order, PaymentProcessStatus
    from keel.notification.tasks import save_pg_response, save_payment_status
    from keel.account.mongo_models import PgLogs
    from keel.plus.models import PlusPlans

    payment_required = True
    user = request.user
    is_sbig = False
    if user.email:
        uemail = user.email
    else:
        uemail = "dummyemail@docprime.com"

    if request.data and request.data.get('utm_sbi_tags') and request.data.get('utm_sbi_tags').get('utm_source') == 'sbi_utm':
        is_sbig = True

    if is_sbig:
        base_url = settings.SBIG_BASE_URL
        surl = base_url + '/api/v1/user/transaction/save?sbig=true'
        furl = base_url + '/api/v1/user/transaction/save?sbig=true'
    else:
        base_url = "https://{}".format(request.get_host())
        surl = base_url + '/api/v1/user/transaction/save'
        furl = base_url + '/api/v1/user/transaction/save'

    profile = user.get_default_profile()
    profile_name = ""
    paytmMsg = ''
    if profile:
        profile_name = profile.name

    orders_list = list()

    for order in orders:

        if order.product_id == Order.GOLD_PRODUCT_ID:
            isPreAuth = '0'
            plus_plan_id = order.action_data.get('plus_plan')
            plus_plan = PlusPlans.objects.filter(id=plus_plan_id).first()
            if not plus_plan:
                raise Exception('Invalid pg transaction as plus plan is not found.')
            proposer = plus_plan.proposer
            plus_merchant_code = proposer.merchant_code

            if not profile:
                if order.action_data.get('profile_detail'):
                    profile_name = order.action_data.get('profile_detail').get('name', "")

        temp_product_id = order.product_id

        discountedAmnt = ''

        usedPgCoupons = order.used_pgspecific_coupons
        if usedPgCoupons and usedPgCoupons[0].payment_option:
            couponCode = usedPgCoupons[0].code
            couponPgMode = get_coupon_pg_mode(usedPgCoupons[0])
            discountedAmnt = str(round(decimal.Decimal(order.amount), 2))
            txAmount = str(round(decimal.Decimal(order.get_amount_without_pg_coupon), 2))
        else:
            txAmount = str(round(decimal.Decimal(order.amount), 2))

        order_dict = {
            "orderId": order.id,
            "productId": temp_product_id,
            "name": profile_name,
            "holdPayment": "false",
            "txAmount": txAmount,
            "insurerCode": settings.GOLD_MERCHANT_CODE if temp_product_id == Order.GOLD_PRODUCT_ID else '',
            "refOrderId": "",
            "refOrderNo": "",
            "discountedAmnt": discountedAmnt
            }

        if not order_dict['insurerCode']:
            del order_dict['insurerCode']

        if Decimal(txAmount) > Decimal(0):
            orders_list.append(order_dict)

    pgdata = {
        "custId": user.id,
        "mobile": user.phone_number,
        "email": uemail,
        "surl": surl,
        "furl": furl,
        "isPreAuth": "0",
        "paytmMsg": paytmMsg,
        "couponCode": '',
        "couponPgMode": '',
    }

    flatten_dict = copy.deepcopy(pgdata)

    order_count = 0
    for od in orders_list:
        for k in od.keys():
            key = str(k) + "[%d]" % order_count

            if str(od[k]):
                flatten_dict[key] = str(od[k])

        order_count += 1

    secret_key, client_key = get_pg_secret_client_key(orders[0])
    filtered_pgdata = {k: v for k, v in flatten_dict.items() if v is not None and v != ''}
    flatten_dict.clear()
    flatten_dict.update(filtered_pgdata)
    pgdata['hash'] = PgTransaction.create_pg_hash(flatten_dict, secret_key, client_key)
    pgdata['is_single_flow'] = True

    order_ids = list(map(lambda x: x['orderId'], orders_list))
    args = {'user_id': user.id, 'order_ids': order_ids, 'source': 'ORDER_CREATE'}
    save_payment_status.apply_async((PaymentProcessStatus.INITIATE, args), eta=timezone.localtime(),)
    if settings.SAVE_LOGS:
        save_pg_response.apply_async((PgLogs.TXN_REQUEST, order_ids, None, None, pgdata, user.id), eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
    pgdata['items'] = orders_list
    return pgdata, payment_required


def payment_details(request, order):
    from keel.authentication.models import UserProfile
    from keel.insurance.models import InsurancePlans
    from keel.account.models import PgTransaction, Order, PaymentProcessStatus
    from keel.notification.tasks import save_pg_response, save_payment_status
    from keel.account.mongo_models import PgLogs
    from keel.plus.models import PlusPlans

    payment_required = True
    user = request.user
    is_sbig = False
    if user.email:
        uemail = user.email
    else:
        uemail = "dummyemail@docprime.com"

    if request.data and request.data.get('utm_sbi_tags') and request.data.get('utm_sbi_tags').get('utm_tags') and request.data.get('utm_sbi_tags').get('utm_tags').get('utm_source') == 'sbi_utm':
        is_sbig = True

    if is_sbig:
        base_url = settings.SBIG_BASE_URL
        surl = base_url + '/api/v1/user/transaction/save?sbig=true'
        furl = base_url + '/api/v1/user/transaction/save?sbig=true'
    else:
        base_url = "https://{}".format(request.get_host())
        surl = base_url + '/api/v1/user/transaction/save'
        furl = base_url + '/api/v1/user/transaction/save'

    isPreAuth = '1'
    profile = user.get_default_profile()
    profile_name = ""
    paytmMsg = ''
    if profile:
        profile_name = profile.name

    insurer_code = None
    plus_merchant_code = None
    if order.product_id == Order.INSURANCE_PRODUCT_ID:
        isPreAuth = '0'
        insurance_plan_id = order.action_data.get('insurance_plan')
        insurance_plan = InsurancePlans.objects.filter(id=insurance_plan_id).first()
        if not insurance_plan:
            raise Exception('Invalid pg transaction as insurer plan is not found.')
        insurer = insurance_plan.insurer
        insurer_code = insurer.insurer_merchant_code

        if not profile:
            if order.action_data.get('profile_detail'):
                profile_name = order.action_data.get('profile_detail').get('name', "")

    if order.product_id in [Order.VIP_PRODUCT_ID, Order.GOLD_PRODUCT_ID]:
        isPreAuth = '0'
        plus_plan_id = order.action_data.get('plus_plan')
        plus_plan = PlusPlans.objects.filter(id=plus_plan_id).first()
        if not plus_plan:
            raise Exception('Invalid pg transaction as plus plan is not found.')
        proposer = plus_plan.proposer
        # plus_merchant_code = proposer.merchant_code
        if order.product_id == Order.VIP_PRODUCT_ID:
            plus_merchant_code = settings.VIP_MERCHANT_CODE
        elif order.product_id == Order.GOLD_PRODUCT_ID:
            plus_merchant_code = settings.GOLD_MERCHANT_CODE
        else:
            plus_merchant_code = ""

        if not profile:
            if order.action_data.get('profile_detail'):
                profile_name = order.action_data.get('profile_detail').get('name', "")

    if order.product_id in [Order.SUBSCRIPTION_PLAN_PRODUCT_ID, Order.CHAT_PRODUCT_ID, Order.PROVIDER_ECONSULT_PRODUCT_ID]:
        isPreAuth = '0'

    if isPreAuth == '1':
        first_slot = None
        if order.is_parent():
            for ord in order.orders.all():
                if ord.action_data:
                    if ord.action_data.get('time_slot_start'):
                        ord_slot = ord.action_data.get('time_slot_start')
                    else:
                        first_test_slot = None
                        test_time_slots = ord.action_data.get('test_time_slots')
                        for test_time_slot in test_time_slots:
                            ord_test_slot = None
                            if test_time_slot.get('time_slot_start'):
                                ord_test_slot = test_time_slot.get('time_slot_start')
                            if not first_test_slot and ord_test_slot:
                                first_test_slot = parse_datetime(ord_test_slot)
                            if first_test_slot > parse_datetime(ord_test_slot):
                                first_test_slot = parse_datetime(ord_test_slot)
                        ord_slot = str(first_test_slot)

                if not first_slot and ord_slot:
                    first_slot = parse_datetime(ord_slot)
                if first_slot > parse_datetime(ord_slot):
                    first_slot = parse_datetime(ord_slot)

        else:
            isPreAuth = '0'
        if first_slot:
            if first_slot < (timezone.now() + timedelta(hours=int(settings.PAYMENT_AUTO_CAPTURE_DURATION))):
                paytmMsg = 'Your payment will be deducted from Paytm wallet on appointment completion.'

    temp_product_id = order.product_id

    couponCode = ''
    couponPgMode = ''
    discountedAmnt = ''

    # if order.is_cod_order:
    #     txAmount = str(round(decimal.Decimal(order.get_deal_price_without_coupon), 2))
    # else:
    usedPgCoupons = order.used_pgspecific_coupons
    if usedPgCoupons and usedPgCoupons[0].payment_option:
        couponCode = usedPgCoupons[0].code
        couponPgMode = get_coupon_pg_mode(usedPgCoupons[0])
        discountedAmnt = str(round(decimal.Decimal(order.amount), 2))
        txAmount = str(round(decimal.Decimal(order.get_amount_without_pg_coupon), 2))
    else:
        txAmount = str(round(decimal.Decimal(order.amount), 2))


    pgdata = {
        'custId': user.id,
        'mobile': user.phone_number,
        'email': uemail,
        'productId': temp_product_id,
        'surl': surl,
        'furl': furl,
        'referenceId': "",
        'orderId': order.id,
        'name': profile_name,
        'txAmount': txAmount,
        'holdPayment': 0,
        'couponCode': couponCode,
        'couponPgMode': couponPgMode,
        'discountedAmnt': discountedAmnt,
        'isPreAuth': isPreAuth,
        'paytmMsg': paytmMsg
    }

    if insurer_code:
        pgdata['insurerCode'] = insurer_code

    if plus_merchant_code:
        pgdata['insurerCode'] = plus_merchant_code

    plus_user = user.active_plus_user
    is_partial_vip_enabled = False
    vip_order_transaction = None
    parent_product_id = None
    if plus_user and plus_user.order:
        transactions = plus_user.order.getTransactions()
        parent_product_id = order.CORP_VIP_PRODUCT_ID if plus_user.plan.is_corporate else order.VIP_PRODUCT_ID
        for ord in order.orders.all():
            from keel.doctor.models import OpdAppointment
            if ord.action_data and ord.action_data.get('payment_type') == OpdAppointment.VIP and transactions:
                vip_order_transaction = transactions[0]
                is_partial_vip_enabled = True
        if is_partial_vip_enabled and transactions and vip_order_transaction and parent_product_id:
            pgdata['refOrderId'] = str(vip_order_transaction.order_id)
            pgdata['refOrderNo'] = str(vip_order_transaction.order_no)
            pgdata['parentProductId'] = str(parent_product_id)

    secret_key, client_key = get_pg_secret_client_key(order)
    filtered_pgdata = {k: v for k, v in pgdata.items() if v is not None and v != ''}
    pgdata.clear()
    pgdata.update(filtered_pgdata)
    pgdata['hash'] = PgTransaction.create_pg_hash(pgdata, secret_key, client_key)

    args = {'user_id': user.id, 'order_id': order.id, 'source': 'ORDER_CREATE'}
    save_payment_status.apply_async((PaymentProcessStatus.INITIATE, args), eta=timezone.localtime(),)
    if settings.SAVE_LOGS:
        save_pg_response.apply_async((PgLogs.TXN_REQUEST, order.id, None, None, pgdata, user.id), eta=timezone.localtime(), queue=settings.RABBITMQ_LOGS_QUEUE)
    # print(pgdata)
    return pgdata, payment_required


def pg_seamless_hash(order, order_no):
    from keel.account.models import PgTransaction
    secret_key, client_key = get_pg_secret_client_key(order)
    orderData = {
        "orderId": order.id,
        "orderNo": order_no
    }
    pg_hash = PgTransaction.create_pg_hash(orderData, secret_key, client_key)
    return pg_hash

def get_pg_secret_client_key(order):
    from keel.account.models import Order
    secret_key = client_key = ""

    if order.product_id in [Order.DOCTOR_PRODUCT_ID, Order.SUBSCRIPTION_PLAN_PRODUCT_ID,  Order.CHAT_PRODUCT_ID, Order.PROVIDER_ECONSULT_PRODUCT_ID, Order.VIP_PRODUCT_ID, Order.GOLD_PRODUCT_ID, Order.CORP_VIP_PRODUCT_ID]:
        secret_key = settings.PG_SECRET_KEY_P1
        client_key = settings.PG_CLIENT_KEY_P1
    elif order.product_id == Order.LAB_PRODUCT_ID:
        secret_key = settings.PG_SECRET_KEY_P2
        client_key = settings.PG_CLIENT_KEY_P2
    elif order.product_id == Order.INSURANCE_PRODUCT_ID:
        secret_key = settings.PG_SECRET_KEY_P3
        client_key = settings.PG_CLIENT_KEY_P3

    return [secret_key, client_key]

def get_coupon_pg_mode(coupon):
    couponPgMode = None
    payment_option = coupon.payment_option
    if payment_option.action == 'DC' and payment_option.payment_gateway == 'paytm':
        couponPgMode = 'dcpt'
    elif payment_option.action == 'CC' and payment_option.payment_gateway == 'paytm':
        couponPgMode = 'ccpt'
    elif payment_option.action == 'NB' and payment_option.payment_gateway == 'paytm':
        couponPgMode = 'nbpt'
    elif payment_option.action == 'UPI' and payment_option.payment_gateway == 'payu':
        couponPgMode = 'puUPI'
    elif payment_option.action == 'PPI' and payment_option.payment_gateway == 'payu':
        couponPgMode = 'puAmz'
    elif payment_option.action == 'PPI' and payment_option.payment_gateway == 'paytm':
        couponPgMode = 'papt'
    elif payment_option.action == 'PPI' and payment_option.payment_gateway == 'olamoney':
        couponPgMode = 'ola'

    return couponPgMode

def get_location(lat, long):
    pnt = None
    if long and lat:
        point_string = 'POINT(' + str(long) + ' ' + str(lat) + ')'
        pnt = GEOSGeometry(point_string, srid=4326)
    return pnt


def get_time_delta_in_minutes(last_visit_time):
    minutes = None
    time_format = '%Y-%m-%d %H:%M:%S'
    current_time_string = datetime.datetime.strftime(datetime.datetime.now(), time_format)
    last_time_object = datetime.datetime.strptime(last_visit_time, time_format)
    current_object = datetime.datetime.strptime(current_time_string, time_format)
    delta = current_object - last_time_object
    #print(delta)
    #if delta:
    minutes = delta.seconds / 60
    return minutes


def aware_time_zone(date_time_field):
    date = timezone.localtime(date_time_field, pytz.timezone(settings.TIME_ZONE))
    return date


def resolve_address(address_obj):
    address_string = ""
    address_dict = dict()
    if not isinstance(address_obj, dict):
        address_dict = vars(address_dict)
    else:
        address_dict = address_obj

    if address_dict.get("address"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["address"])
    if address_dict.get("land_mark"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["land_mark"])
    if address_dict.get("locality"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["locality"])
    if address_dict.get("pincode"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["pincode"])

    return address_string


def thyrocare_resolve_address(address_obj):
    address_string = ""
    address_dict = dict()
    if not isinstance(address_obj, dict):
        address_dict = vars(address_dict)
    else:
        address_dict = address_obj

    if address_dict.get("address"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["address"])
    if address_dict.get("locality"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["locality"])
    if address_dict.get("pincode"):
        if address_string:
            address_string += ", "
        address_string += str(address_dict["pincode"])

    return address_string


def generate_short_url(url):
    from keel.web import models as web_models
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
    tiny_url = web_models.TinyUrl.objects.filter(short_code=random_string).first()
    if tiny_url:
        return tiny_url
    tiny_url = web_models.TinyUrl.objects.create(original_url=url, short_code=random_string)
    return tiny_url.get_tiny_url()


def readable_status_choices(product):
    from keel.account.models import Order
    from keel.doctor.models import OpdAppointment
    from keel.diagnostic.models import LabAppointment
    status_choices = dict()
    if product == Order.DOCTOR_PRODUCT_ID:
        for k, v in OpdAppointment.STATUS_CHOICES:
            status_choices[k] = v
    elif product == Order.LAB_PRODUCT_ID:
        for k, v in LabAppointment.STATUS_CHOICES:
            status_choices[k] = v
    return status_choices


def get_lab_search_details(entity, req_params):
    params_dict = copy.deepcopy(req_params)
    if entity.get('location_json'):
            if entity.get('location_json').get('sublocality_longitude'):
                params_dict['long'] = entity.get('location_json').get('sublocality_longitude')
            elif entity.get('location_json').get('locality_longitude'):
                params_dict['long'] = entity.get('location_json').get('locality_longitude')

            if entity.get('location_json').get('sublocality_latitude'):
                params_dict['lat'] = entity.get('location_json').get('sublocality_latitude')
            elif entity.get('location_json').get('locality_latitude'):
                params_dict['lat'] = entity.get('location_json').get('locality_latitude')

    return params_dict


def doctor_query_parameters(entity, req_params):
    params_dict = copy.deepcopy(req_params)
    if entity.sublocality_latitude:
        params_dict["latitude"] = entity.sublocality_latitude
    elif entity.locality_latitude:
        params_dict["latitude"] = entity.locality_latitude
    if entity.sublocality_longitude:
        params_dict["longitude"] = entity.sublocality_longitude
    elif entity.locality_longitude:
        params_dict["longitude"] = entity.locality_longitude
    if entity.ipd_procedure_id:
        params_dict["ipd_procedure_ids"] = str(entity.ipd_procedure_id)

    # if entity_params.get("location_json"):
    #     if entity_params["location_json"].get("sublocality_latitude"):
    #         params_dict["latitude"] = entity_params["location_json"]["sublocality_latitude"]
    #     elif entity_params["location_json"].get("locality_latitude"):
    #         params_dict["latitude"] = entity_params["location_json"]["locality_latitude"]
    #
    #     if entity_params["location_json"].get("sublocality_longitude"):
    #         params_dict["longitude"] = entity_params["location_json"]["sublocality_longitude"]
    #     elif entity_params["location_json"].get("locality_longitude"):
    #         params_dict["longitude"] = entity_params["location_json"]["locality_longitude"]
    if entity.specialization_id:
        params_dict["specialization_ids"] = str(entity.specialization_id)
    else:
        params_dict["specialization_ids"] = ''

    params_dict["condition_ids"] = ''
    params_dict["procedure_ids"] = ''
    params_dict["procedure_category_ids"] = ''

    return params_dict


def form_pg_refund_data(refund_objs):
    from keel.account.models import PgTransaction
    pg_data = list()
    for data in refund_objs:
        if data.pg_transaction:
            params = {
                "user": str(data.user.id),
                "orderNo": str(data.pg_transaction.order_no),
                "orderId": str(data.pg_transaction.order_id),
                "refundAmount": str(data.refund_amount),
                "refNo": str(data.id),
            }
            secret_key = settings.PG_SECRET_KEY_REFUND
            client_key = settings.PG_CLIENT_KEY_REFUND
            params["checkSum"] = PgTransaction.create_pg_hash(params, secret_key, client_key)
            pg_data.append(params)
    return pg_data


class CouponsMixin(object):

    def validate_user_coupon(self, **kwargs):
        from keel.coupon.models import Coupon
        from keel.doctor.models import OpdAppointment
        from keel.diagnostic.models import LabAppointment
        from keel.subscription_plan.models import UserPlanMapping
        from keel.plus.models import PlusUser
        from keel.cart.models import Cart

        user = kwargs.get("user")
        coupon_obj = kwargs.get("coupon_obj")
        profile = kwargs.get("profile")
        cart_item = kwargs.get("cart_item")

        if coupon_obj:
            if coupon_obj.is_user_specific and not user.is_authenticated:
                return {"is_valid": False, "used_count": 0}

            if isinstance(self, OpdAppointment) and coupon_obj.type not in [Coupon.DOCTOR, Coupon.ALL]:
                return {"is_valid": False, "used_count": None}
            elif isinstance(self, LabAppointment) and coupon_obj.type not in [Coupon.LAB, Coupon.ALL]:
                return {"is_valid": False, "used_count": None}
            elif isinstance(self, UserPlanMapping) and coupon_obj.type not in [Coupon.SUBSCRIPTION_PLAN, Coupon.ALL]:
                return {"is_valid": False, "used_count": None}
            elif isinstance(self, PlusUser) and coupon_obj.type not in [Coupon.VIP, Coupon.GOLD]:
                return {"is_valid": False, "used_count": None}

            diff_days = (timezone.now() - (coupon_obj.start_date or coupon_obj.created_at)).days
            if  diff_days < 0 or diff_days > coupon_obj.validity:
                return {"is_valid": False, "used_count": None}

            allowed_coupon_count = coupon_obj.count

            if coupon_obj.is_user_specific:
                allowed_coupon = coupon_obj.user_specific_coupon.filter(user=user).exists()
                if not allowed_coupon:
                    return {"is_valid": False, "used_count": None}

            # check if a user is new i.e user has done any appointments
            if user.is_authenticated:
                if profile:
                    user_profile = user.profiles.filter(id=profile.id).first()
                else:
                    user_profile = user.profiles.filter(is_default_user=True).first()
                if user_profile:
                    user_age = user_profile.get_age()
                else:
                    user_age = None

                if coupon_obj.new_user_constraint and not self.is_user_first_time(user):
                    return {"is_valid": False, "used_count": 0}

                # TODO - COUPON APPLICABLE EVERY 5th or 3rd APPOINTMENT
                # if coupon_obj.step_count != 1:
                #     user_opd_completed = OpdAppointment.objects.filter(user=user,
                #                                                        status__in=[OpdAppointment.COMPLETED]).count()
                #     user_lab_completed = LabAppointment.objects.filter(user=user,
                #                                                        status__in=[LabAppointment.COMPLETED]).count()
                #     if ((user_opd_completed + user_lab_completed + 1) % coupon_obj.step_count != 0):
                #         return {"is_valid": False, "used_count": None}

                if coupon_obj.gender and (not user_profile or coupon_obj.gender != user_profile.gender):
                    return {"is_valid": False, "used_count": None}

                if ( (coupon_obj.age_start and (not user_age or coupon_obj.age_start > user_age))
                        or (coupon_obj.age_end and (not user_age or coupon_obj.age_end < user_age)) ):
                    return {"is_valid": False, "used_count": None}

                payment_option_filter = Cart.get_pg_if_pgcoupon(user, cart_item)
                if payment_option_filter and coupon_obj.payment_option and coupon_obj.payment_option.id != payment_option_filter.id:
                    return {"is_valid": False, "used_count": 0}

            count = coupon_obj.used_coupon_count(user, cart_item)
            total_used_count = coupon_obj.total_used_count

            if coupon_obj.is_user_specific and user:
                user_specefic = UserSpecificCoupon.objects.filter(user=user, coupon=coupon_obj).first()
                if user_specefic and count >= user_specefic.count:
                    return {"is_valid": False, "used_count": count}

            # if coupon is random coupon
            if hasattr(coupon_obj, 'is_random') and coupon_obj.is_random:
                random_count = coupon_obj.random_coupon_used_count(None, coupon_obj.random_coupon_code, cart_item)
                if random_count > 0:
                    return {"is_valid": False, "used_count": random_count}
                else:
                    return {"is_valid": True, "used_count": random_count}

            if (coupon_obj.count is None or count < coupon_obj.count) and (coupon_obj.total_count is None or total_used_count < coupon_obj.total_count):
                return {"is_valid": True, "used_count": count}
            else:
                return {"is_valid": False, "used_count": count}
        else:
            return {"is_valid": False, "used_count": None}

    def validate_product_coupon(self, **kwargs):
        from keel.diagnostic.models import Lab
        from keel.account.models import Order
        from keel.coupon.models import Coupon

        import re

        coupon_obj = kwargs.get("coupon_obj")

        is_valid = True

        if not coupon_obj:
            return False

        # product_id = kwargs.get("product_id")

        # if product_id == Order.LAB_PRODUCT_ID:
        lab = kwargs.get("lab")
        tests = kwargs.get("test", [])
        doctor = kwargs.get("doctor")
        hospital = kwargs.get("hospital")
        procedures = kwargs.get("procedures", [])
        plan = kwargs.get("plan")
        gold_vip_plan_id = kwargs.get('gold_vip_plan_id')

        if plan:
            if coupon_obj.type in [Coupon.ALL, Coupon.SUBSCRIPTION_PLAN] \
                and coupon_obj.plan.filter(id=plan.id).exists():
                    return True
            return False

        if gold_vip_plan_id:
            if coupon_obj.type in [Coupon.VIP, Coupon.GOLD]:
                vip_gold_plans = coupon_obj.vip_gold_plans.all()
                if not vip_gold_plans:
                    return True
                elif vip_gold_plans.filter(id=gold_vip_plan_id).exists():
                    return True
            return False

        if coupon_obj.lab and coupon_obj.lab != lab:
            return False

        if coupon_obj.lab_network and (not lab or lab.network!=coupon_obj.lab_network):
            return False

        if coupon_obj.test.exists():
            if tests:
                count = coupon_obj.test.filter(id__in=[t.id for t in tests]).count()
                if count == 0:
                    return False
            else:
                return False

        if coupon_obj.test_categories.exists():
            if tests:
                category_ids = []
                for test in tests:
                    categories = test.categories.values_list("id", flat=True)
                    category_ids.extend(categories)
                category_ids = list(set(category_ids))
                test_cat_count = coupon_obj.test_categories.filter(id__in=category_ids).count()
                if test_cat_count == 0:
                    return False
            else:
                return False

        if coupon_obj.cities:
            if (lab and re.search(lab.city, coupon_obj.cities, re.IGNORECASE)) or not lab:
                return False
            if (hospital and re.search(hospital.city, coupon_obj.cities, re.IGNORECASE)) or not hospital:
                return False

        if coupon_obj.doctors.exists() and (not doctor or doctor not in coupon_obj.doctors.all()):
            return False

        if doctor and (coupon_obj.doctors_exclude.exists() and (not doctor or doctor in coupon_obj.doctors_exclude.all())):
            return False

        if coupon_obj.hospitals.exists() and (not hospital or hospital not in coupon_obj.hospitals.all()):
            return False

        if hospital and (coupon_obj.hospitals_exclude.exists() and (not hospital or hospital in coupon_obj.hospitals_exclude.all())):
            return False

        if coupon_obj.procedures.exists():
            if procedures:
                procedure_count = coupon_obj.procedures.filter(id__in=[proc.id for proc in procedures]).count()
                if procedure_count == 0:
                    return False
            else:
                return False

        if coupon_obj.procedure_categories.exists():
            if procedures:
                category_ids = []
                for procedure in procedures:
                    categories = procedure.categories.values_list("id", flat=True)
                    category_ids.extend(categories)
                category_ids = list(set(category_ids))
                procedure_cat_count = coupon_obj.procedure_categories.filter(id__in=category_ids).count()
                if procedure_cat_count == 0:
                    return False
            else:
                return False

        if coupon_obj.specializations.exists():
            if doctor:
                spec_count = coupon_obj.specializations.filter(
                    id__in=doctor.doctorpracticespecializations.values_list('specialization', flat=True)).count()
                if spec_count == 0:
                    return False
            else:
                return False

        return is_valid


    def get_discount(self, coupon_obj, price):

        discount = 0

        if coupon_obj:
            if coupon_obj.min_order_amount is not None and price < coupon_obj.min_order_amount:
                return 0

            if coupon_obj.flat_discount is not None:
                discount = coupon_obj.flat_discount
            elif coupon_obj.percentage_discount is not None:
                discount = math.floor(price * coupon_obj.percentage_discount / 100)

            if coupon_obj.max_discount_amount is not None:
                discount = min(coupon_obj.max_discount_amount, discount)

            if discount > price:
                discount = price

            return discount
        else:
            return 0

    def get_applicable_tests_with_total_price(self, **kwargs):
        from keel.diagnostic.models import AvailableLabTest

        coupon_obj = kwargs.get("coupon_obj")
        lab = kwargs.get("lab")
        test_ids = kwargs.get("test_ids")

        queryset = AvailableLabTest.objects.filter(lab_pricing_group__labs=lab, test__in=test_ids)
        if coupon_obj.test.exists():
            queryset = queryset.filter(test__in=coupon_obj.test.all())

        total_price = 0
        for test in queryset:
            if test.custom_deal_price is not None:
                total_price += test.custom_deal_price
            else:
                total_price += test.computed_deal_price

        return {"total_price": total_price}

    def get_applicable_tests_with_total_price_v2(self, **kwargs):
        from keel.diagnostic.models import AvailableLabTest

        lab = kwargs.get("lab")
        test_ids = kwargs.get("test_ids")

        queryset = AvailableLabTest.objects.filter(lab_pricing_group__labs=lab, test__in=test_ids)

        total_price = 0
        for test in queryset:
            if test.custom_deal_price is not None:
                total_price += test.custom_deal_price
            else:
                total_price += test.computed_deal_price

        return {"total_price": total_price}

    def get_applicable_procedures_with_total_price(self, **kwargs):
        from keel.procedure.models import DoctorClinicProcedure

        coupon_obj = kwargs.get("coupon_obj")
        doctor = kwargs.get("doctor")
        hospital = kwargs.get("hospital")
        procedures = kwargs.get("procedures")

        queryset = DoctorClinicProcedure.objects.filter(doctor_clinic__doctor=doctor, doctor_clinic__hospital=hospital, procedure__in=procedures)
        if coupon_obj.procedures.exists():
            queryset = queryset.filter(procedure__in=coupon_obj.procedures.all())

        total_price = 0
        for procedure in queryset:
            total_price += procedure.deal_price

        return {"total_price": total_price}

    def get_applicable_procedures_with_total_price_v2(self, **kwargs):
        from keel.procedure.models import DoctorClinicProcedure

        doctor = kwargs.get("doctor")
        hospital = kwargs.get("hospital")
        procedures = kwargs.get("procedures")

        queryset = DoctorClinicProcedure.objects.filter(doctor_clinic__doctor=doctor, doctor_clinic__hospital=hospital, procedure__in=procedures)

        total_price = 0
        for procedure in queryset:
            total_price += procedure.deal_price

        return {"total_price": total_price}

    def is_user_first_time(self, user):
        from keel.doctor.models import OpdAppointment
        from keel.diagnostic.models import LabAppointment

        new_user = True
        all_appointments = LabAppointment.objects.filter(Q(user=user), ~Q(status__in=[LabAppointment.CANCELLED])).count() + OpdAppointment.objects.filter(Q(user=user), ~Q(status__in=[OpdAppointment.CANCELLED])).count()
        if all_appointments > 0:
            new_user = False
        return new_user

    def has_lensfit_coupon_used(self):
        return self.coupon.filter(is_lensfit=True).exists()


class TimeSlotExtraction(object):
    MORNING = "AM"
    # AFTERNOON = "Afternoon"
    EVENING = "PM"
    TIME_SPAN = 30  # In minutes
    TIME_SPAN_NUM = 0.5
    DOCTOR_MAX_TIMING = 20.0
    DOCTOR_BOOK_AFTER = 1
    LAB_BOOK_AFTER = 2
    LAB_HOMEPICKUP_BOOK_AFTER = 4
    NO_OF_UPCOMING_SLOTS = 3
    timing = dict()
    price_available = dict()
    time_division = list()
    time_division.append(MORNING)
    time_division.append(EVENING)

    def __init__(self):
        for i in range(7):
            self.timing[i] = dict()
            self.price_available[i] = dict()

    def form_time_slots(self, day, start, end, price=None, is_available=True,
                        deal_price=None, mrp=None, cod_deal_price=None, is_doctor=False, on_call=1):
        start = Decimal(str(start))
        end = Decimal(str(end))
        time_span = self.TIME_SPAN

        float_span = (Decimal(time_span) / Decimal(60))
        if not self.timing[day].get('timing'):
            self.timing[day]['timing'] = dict()
            self.timing[day]['timing'][self.MORNING] = OrderedDict()
            # self.timing[day]['timing'][self.AFTERNOON] = OrderedDict()
            self.timing[day]['timing'][self.EVENING] = OrderedDict()
        temp_start = start
        while temp_start <= end:
            # day_slot, am_pm = self.get_day_slot(temp_start)
            day_slot = self.get_day_slot(temp_start)
            # time_str = self.form_time_string(temp_start, am_pm)
            time_str = self.form_time_string(temp_start)
            self.timing[day]['timing'][day_slot][temp_start] = time_str
            price_available = {"price": price, "is_available": is_available}
            if is_doctor:
                price_available.update({
                    "mrp": mrp,
                    "deal_price": deal_price,
                    "cod_deal_price": cod_deal_price
                })
            price_available.update({
                "on_call": bool(on_call==2)
            })
            self.price_available[day][temp_start] = price_available
            temp_start += float_span

    def get_day_slot(self, time):
        # am = 'AM'
        # pm = 'PM'
        if time < 12:
            return self.MORNING  #, am
        # elif time < 16:
        #     return self.AFTERNOON, pm
        else:
            return self.EVENING  #, pm

    def form_time_string(self, time, am_pm=''):
        time = form_dc_time(time, am_pm)
        return time

    def get_timing_list(self):
        whole_timing_data = dict()
        for i in range(7):
            whole_timing_data[i] = list()
            pa = self.price_available[i]
            if self.timing[i].get('timing'):
                # data = self.format_data(self.timing[i]['timing'][self.MORNING], pa)
                whole_timing_data[i].append(self.format_data(self.timing[i]['timing'][self.MORNING], self.MORNING, pa))
                # whole_timing_data[i].append(self.format_data(self.timing[i]['timing'][self.AFTERNOON], self.AFTERNOON, pa))
                whole_timing_data[i].append(self.format_data(self.timing[i]['timing'][self.EVENING], self.EVENING, pa))

        return whole_timing_data

    def get_timing_slots(self, date, leaves, booking_details, is_thyrocare=False):
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        day = date.weekday()
        booking_type = booking_details.get('type')
        if booking_type == 'integration':
            total_leave_list = []
        elif booking_type == "doctor":
            total_leave_list = self.get_doctor_leave_list(leaves)
        else:
            total_leave_list = self.get_lab_leave_list(leaves)
        whole_timing_data = OrderedDict()
        booking_details['total_leave_list'] = total_leave_list

        j = 0
        if is_thyrocare:
            self.get_slots(date, day, j, whole_timing_data, booking_details, is_thyrocare)
        else:
            for k in range(int(settings.NO_OF_WEEKS_FOR_TIME_SLOTS)):
                for i in range(7):
                    if k == 0:
                        if i >= day:
                            self.get_slots(date, i, j, whole_timing_data, booking_details, is_thyrocare)
                            j = j + 1
                    else:
                        self.get_slots(date, i, j, whole_timing_data, booking_details, is_thyrocare)
                        j = j + 1
        return whole_timing_data

    def get_slots(self, date, i, j, whole_timing_data, booking_details, is_thyrocare):
        converted_date = (date + datetime.timedelta(days=j))
        readable_date = converted_date.strftime("%Y-%m-%d")
        booking_details['date'] = converted_date
        total_leave_list = booking_details.get('total_leave_list')
        if converted_date in total_leave_list:
            whole_timing_data[readable_date] = list()
        else:
            whole_timing_data[readable_date] = list()
            pa = self.price_available[i]

            if self.timing[i].get('timing'):
                am_timings = self.format_data_new(self.timing[i]['timing'][self.MORNING], self.MORNING, pa, booking_details, is_thyrocare)
                pm_timings = self.format_data_new(self.timing[i]['timing'][self.EVENING], self.EVENING, pa, booking_details, is_thyrocare)
                if len(am_timings.get('timing')) == 0 and len(pm_timings.get('timing')) == 0:
                    # whole_timing_data[readable_date].append({})
                    pass
                else:
                    whole_timing_data[readable_date].append(am_timings)
                    whole_timing_data[readable_date].append(pm_timings)

    def get_doctor_leave_list(self, leaves):
        total_leaves = list()
        doctor_leaves = leaves.get('doctor')
        global_leaves = leaves.get('global')
        for dl in doctor_leaves:
            start_date = dl.get('start_date')
            end_date = dl.get('end_date')
            if start_date == end_date:
                total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            else:
                delta = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date, '%Y-%m-%d')
                total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                for i in range(delta.days + 1):
                    total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(i))
        for gl in global_leaves:
            start_date = gl.get('start_date')
            end_date = gl.get('end_date')
            if start_date == end_date:
                total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            else:
                delta = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date, '%Y-%m-%d')
                for i in range(delta.days + 1):
                    total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(i))
        doc_leave_set = set(total_leaves)
        final_leaves = list(doc_leave_set)
        return final_leaves

    def get_lab_leave_list(self, leaves):
        total_leaves = list()
        for gl in leaves:
            start_date = gl.get('start_date')
            end_date = gl.get('end_date')
            if start_date == end_date:
                total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
            else:
                delta = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.datetime.strptime(start_date,
                                                                                                      '%Y-%m-%d')
                total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                for i in range(delta.days + 1):
                    total_leaves.append(datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(i))
        lab_leave_set = set(total_leaves)
        final_leaves = list(lab_leave_set)
        return final_leaves

    def format_data(self, data, day_time, pa):
        data_list = list()
        for k, v in data.items():
            if 'mrp' in pa[k].keys() and 'deal_price' in pa[k].keys():
                data_list.append({"value": k, "text": v, "price": pa[k]["price"],
                                  "mrp": pa[k]['mrp'], 'deal_price': pa[k]['deal_price'],
                                  "is_available": pa[k]["is_available"], "on_call": pa[k].get("on_call", False)})
            else:
                data_list.append({"value": k, "text": v, "price": pa[k]["price"],
                                  "is_available": pa[k]["is_available"], "on_call": pa[k].get("on_call", False)})
        format_data = dict()
        format_data['type'] = 'AM' if day_time == self.MORNING else 'PM'
        format_data['title'] = day_time
        format_data['timing'] = data_list
        return format_data

    def format_data_new(self, data, day_time, pa, booking_details, is_thyrocare):
        current_date_time = datetime.datetime.now()
        booking_date = booking_details.get('date')
        lab_tomorrow_time = 0.0
        lab_minimum_time = None
        doc_minimum_time = None
        doctor_maximum_timing = 20.0
        if booking_details.get('type') == "doctor":
            if current_date_time.date() == booking_date.date():
                doc_booking_minimum_time = current_date_time + datetime.timedelta(hours=1)
                doc_booking_hours = doc_booking_minimum_time.strftime('%H:%M')
                hours, minutes = doc_booking_hours.split(':')
                mins = int(hours) * 60 + int(minutes)
                doc_minimum_time = mins / 60
        else:
            if is_thyrocare:
                pass
            else:
                is_home_pickup = booking_details.get('is_home_pickup')
                if is_home_pickup:
                    if current_date_time.weekday() == 6:
                        lab_minimum_time = 24.0
                    if current_date_time.hour < 13:
                        lab_booking_minimum_time = current_date_time + datetime.timedelta(hours=4)
                        lab_booking_hours = lab_booking_minimum_time.strftime('%H:%M')
                        hours, minutes = lab_booking_hours.split(':')
                        mins = int(hours) * 60 + int(minutes)
                        lab_minimum_time = mins / 60
                    elif current_date_time.hour >= 13 and current_date_time.hour < 17:
                        lab_minimum_time = 24.0
                    if current_date_time.hour >= 17:
                        lab_minimum_time = 24.0
                        lab_tomorrow_time = 12.0
                else:
                    lab_booking_minimum_time = current_date_time + datetime.timedelta(hours=2)
                    lab_booking_hours = lab_booking_minimum_time.strftime('%H:%M')
                    hours, minutes = lab_booking_hours.split(':')
                    mins = int(hours) * 60 + int(minutes)
                    lab_minimum_time = mins / 60


        data_list = list()
        for k, v in data.items():
            if 'mrp' in pa[k].keys() and 'deal_price' in pa[k].keys():
                if current_date_time.date() == booking_date.date():
                    if pa[k].get('on_call') == False:
                        if k >= float(doc_minimum_time) and k <= doctor_maximum_timing:
                            data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                              "mrp": pa[k]['mrp'], 'deal_price': pa[k]['deal_price'], "cod_deal_price": pa[k]['cod_deal_price'],
                                              "is_available": pa[k]["is_available"], "on_call": pa[k].get("on_call", False)})
                        else:
                            pass
                    else:
                        pass
                else:
                    if k <= doctor_maximum_timing:
                        data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                          "mrp": pa[k]['mrp'], 'deal_price': pa[k]['deal_price'], "cod_deal_price": pa[k]['cod_deal_price'],
                                          "is_available": pa[k]["is_available"],
                                          "on_call": pa[k].get("on_call", False)})
                    else:
                        pass
            else:
                next_date = current_date_time + datetime.timedelta(days=1)
                if current_date_time.date() == booking_date.date():
                    if k >= float(lab_minimum_time):
                        data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                          "is_available": pa[k]["is_available"],
                                          "on_call": pa[k].get("on_call", False)})
                    else:
                        pass
                elif next_date.date() == booking_date.date():
                    if lab_tomorrow_time:
                        if k >= float(lab_tomorrow_time):
                            data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                              "is_available": pa[k]["is_available"],
                                              "on_call": pa[k].get("on_call", False)})
                        else:
                            pass
                    else:
                        data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                          "is_available": pa[k]["is_available"],
                                          "on_call": pa[k].get("on_call", False)})

                else:
                    data_list.append({"value": k, "text": v, "price": pa[k]["price"], "is_price_zero": True if pa[k]["price"] is not None and pa[k]["price"] == 0 else False,
                                      "is_available": pa[k]["is_available"],
                                      "on_call": pa[k].get("on_call", False)})

        format_data = dict()
        format_data['type'] = 'AM' if day_time == self.MORNING else 'PM'
        format_data['title'] = day_time
        format_data['timing'] = data_list
        return format_data

    def initial_start_times(self, is_thyrocare, is_home_pickup, time_slots):
        today_min = None
        tomorrow_min = None
        today_max = None

        now = datetime.datetime.now()
        curr_time = now.hour
        curr_minute = round(round(float(now.minute) / 60, 2) * 2) / 2
        curr_time += curr_minute
        is_sunday = now.weekday() == 6

        # TODO: put time gaps in config
        if is_home_pickup:
            if is_thyrocare:
                today_min = 24
                if curr_time >= 17:
                    tomorrow_min = 24
            else:
                if is_sunday:
                    today_min = 24
                else:
                    if curr_time < 13:
                        today_min = curr_time + 4
                    elif curr_time >= 13:
                        today_min = 24
                if curr_time >= 17:
                    tomorrow_min = 12
        else:
            if not is_thyrocare:
                # add 2 hours gap,
                today_min = curr_time + 2

                # block lab for 2 hours, before last found time slot
                if time_slots and time_slots[now.weekday()]:
                    max_val = 0
                    for s in time_slots[now.weekday()]:
                        if s["timing"]:
                            for t in s["timing"]:
                                max_val = max(t["value"], max_val)
                    if max_val >= 2:
                        today_max = max_val - 2

        return today_min, tomorrow_min, today_max

    def get_upcoming_slots(self, time_slots):
        no_of_slots = TimeSlotExtraction.NO_OF_UPCOMING_SLOTS
        next_day_slot = 0
        upcoming = OrderedDict()
        for key, value in time_slots.items():
            if not value or (not value[0]['timing'] and not value[1]['timing']):
                pass
            else:
                upcoming[key] = list()
                if len(value[0]['timing']) >= no_of_slots:
                    if next_day_slot > 0:
                        range_upto = next_day_slot
                    else:
                        range_upto = no_of_slots

                    for i in range(range_upto):
                        upcoming[str(key)].append(value[0]['timing'][i])

                    next_day_slot = no_of_slots - (len(value[0]['timing']) + next_day_slot)

                elif len(value[0]['timing']) < no_of_slots:
                    if next_day_slot > 0:
                        if next_day_slot >= len(value[0]['timing']):
                            range_upto = len(value[0]['timing'])
                        else:
                            range_upto = next_day_slot

                        for i in range(range_upto):
                            upcoming[str(key)].append(value[0]['timing'][i])

                        remaining = next_day_slot - len(value[0]['timing'])
                        if remaining >= len(value[1]['timing']):
                            range_upto = len(value[1]['timing'])
                        else:
                            range_upto = remaining

                        for i in range(range_upto):
                            upcoming[str(key)].append(value[1]['timing'][i])
                    else:
                        for i in range(len(value[0]['timing'])):
                            upcoming[str(key)].append(value[0]['timing'][i])

                        remaining = no_of_slots - len(value[0]['timing'])
                        if remaining >= len(value[1]['timing']):
                            range_upto = len(value[1]['timing'])
                        else:
                            range_upto = remaining

                        for i in range(range_upto):
                            upcoming[str(key)].append(value[1]['timing'][i])
                    next_day_slot = no_of_slots - (len(value[0]['timing']) + len(value[1]['timing']) + next_day_slot)

                if next_day_slot > 0:
                    pass
                else:
                    return upcoming

    def format_timing_to_datetime_v2(self, timings, total_leaves, booking_details, is_thyrocare=False):
        from keel.doctor.models import DoctorClinicTiming
        check_next_day_minimum_slot = True if timings and isinstance(timings[0], DoctorClinicTiming) else False
        timing_objects = OrderedDict()
        today_date = datetime.date.today()
        today_day = today_date.weekday()
        for k in range(int(settings.NO_OF_WEEKS_FOR_TIME_SLOTS)):
            for i in range(7):
                if not (k == 0 and i < today_day):
                    j = i + (k * 7) - today_day
                    next_slot_date = today_date + datetime.timedelta(j)
                    next_slot_date_str = str(next_slot_date)
                    timing_objects[next_slot_date_str] = list()
                    for data in timings:
                        day = self.get_key_or_field_value(data, 'day')
                        if i == day:
                            start_hour = float(self.get_key_or_field_value(data, 'start', 0.0))
                            if check_next_day_minimum_slot and (today_date + datetime.timedelta(1)) == next_slot_date and datetime.datetime.today().hour >= 20:
                                if start_hour <= 8.5:
                                    start_hour = 8.5
                            end_hour = float(self.get_key_or_field_value(data, 'end', 23.75))
                            time_before_end_hour = end_hour - TimeSlotExtraction.TIME_SPAN_NUM
                            while start_hour <= time_before_end_hour:
                                time_formatted = self.form_dc_time_v2(start_hour)
                                clinic_datetime = datetime.datetime.combine(next_slot_date, time_formatted[0])

                                leave_at_timeslot = False
                                for leave in total_leaves:
                                    if leave.get('start_datetime') <= clinic_datetime <= leave.get('end_datetime'):
                                        leave_at_timeslot = True
                                        break
                                if not leave_at_timeslot:
                                    if len(timing_objects[next_slot_date_str]) < len(self.time_division):
                                        for division in self.time_division:
                                            time_json = dict()
                                            time_json['type'] = division
                                            time_json['title'] = division
                                            time_json['timing'] = list()
                                            timing_objects[next_slot_date_str].append(time_json)
                                    self.format_data_new_v2(timing_objects[next_slot_date_str], clinic_datetime, data, start_hour, time_formatted[1], booking_details, is_thyrocare)
                                start_hour += TimeSlotExtraction.TIME_SPAN_NUM

        return timing_objects

    def form_dc_time_v2(self, time):
        day_time_hour = int(time)
        day_time_min = (time - day_time_hour) * 60

        day_time_hour_am_pm = day_time_hour
        if day_time_hour > 12:
            day_time_hour_am_pm -= 12

        day_time_hour_str_am_pm = str(int(day_time_hour_am_pm))
        if int(day_time_hour_str_am_pm) < 10:
            day_time_hour_str_am_pm = '0' + str(int(day_time_hour_str_am_pm))

        day_time_min_str = str(int(day_time_min))
        if int(day_time_min) < 10:
            day_time_min_str = '0' + str(int(day_time_min))

        time_str_am_pm = day_time_hour_str_am_pm + ":" + day_time_min_str
        time_str = str(day_time_hour) + ":" + day_time_min_str
        time_datetime = datetime.datetime.strptime(time_str, '%H:%M').time()

        return [time_datetime, time_str_am_pm]


    def format_data_new_v2(self, timing_date_obj, clinic_datetime, data, start_hour, start_hour_text, booking_details, is_thyrocare):
        from keel.doctor.models import DoctorClinicTiming
        price = self.get_key_or_field_value(data, 'fees')
        mrp = self.get_key_or_field_value(data, 'mrp')
        deal_price = self.get_key_or_field_value(data, 'deal_price')
        cod_deal_price = data.dct_cod_deal_price() if isinstance(data, DoctorClinicTiming) else False
        data_type = self.get_key_or_field_value(data, 'type', 1)
        on_call = bool(data_type==2)
        is_available = True
        is_doctor = booking_details.get('type') == "doctor"
        current_date_time = datetime.datetime.now()
        booking_date = clinic_datetime
        lab_tomorrow_time = 0.0
        lab_minimum_time = None
        doc_minimum_time = None
        doctor_maximum_timing = TimeSlotExtraction.DOCTOR_MAX_TIMING
        doc_booking_minimum_time = current_date_time
        lab_booking_minimum_time = current_date_time

        if is_doctor:
            if current_date_time.date() == booking_date.date():
                doc_booking_minimum_time = current_date_time + datetime.timedelta(hours=TimeSlotExtraction.DOCTOR_BOOK_AFTER)
                doc_booking_hours = doc_booking_minimum_time.strftime('%H:%M')
                hours, minutes = doc_booking_hours.split(':')
                mins = int(hours) * 60 + int(minutes)
                doc_minimum_time = mins / 60
        else:
            if is_thyrocare:
                pass
            else:
                is_home_pickup = booking_details.get('is_home_pickup')
                if is_home_pickup:
                    if current_date_time.weekday() == 6:
                        lab_minimum_time = 24.0
                    if current_date_time.hour < 13:
                        lab_booking_minimum_time = current_date_time + datetime.timedelta(hours=TimeSlotExtraction.LAB_HOMEPICKUP_BOOK_AFTER)
                        lab_booking_hours = lab_booking_minimum_time.strftime('%H:%M')
                        hours, minutes = lab_booking_hours.split(':')
                        mins = int(hours) * 60 + int(minutes)
                        lab_minimum_time = mins / 60
                    elif current_date_time.hour >= 13 and current_date_time.hour < 17:
                        lab_minimum_time = 24.0
                    if current_date_time.hour >= 17:
                        lab_minimum_time = 24.0
                        lab_tomorrow_time = 12.0
                else:
                    lab_booking_minimum_time = current_date_time + datetime.timedelta(hours=TimeSlotExtraction.LAB_BOOK_AFTER)
                    lab_booking_hours = lab_booking_minimum_time.strftime('%H:%M')
                    hours, minutes = lab_booking_hours.split(':')
                    mins = int(hours) * 60 + int(minutes)
                    lab_minimum_time = mins / 60

        data_list = dict()
        if is_doctor:
            will_doctor_data_append = False
            if current_date_time.date() == booking_date.date():
                if doc_booking_minimum_time.date() == booking_date.date():
                    if on_call == False:
                        if start_hour >= float(doc_minimum_time) and start_hour <= doctor_maximum_timing:
                            will_doctor_data_append = True
                        else:
                            pass
                    else:
                        pass
            else:
                if start_hour <= doctor_maximum_timing:
                    will_doctor_data_append = True
                else:
                    pass

            if will_doctor_data_append:
                data_list = {"value": start_hour, "text": start_hour_text, "price": price, "fees": price, "is_price_zero": True if price is not None and price == 0 else False, "mrp": mrp, 'deal_price': deal_price,
                             "is_available": is_available, "on_call": on_call, "cod_deal_price": cod_deal_price}
        else:
            will_lab_data_append = False
            next_date = current_date_time + datetime.timedelta(days=1)
            if current_date_time.date() == booking_date.date():
                if lab_booking_minimum_time.date() == booking_date.date():
                    if start_hour >= float(lab_minimum_time):
                        will_lab_data_append = True
                    else:
                        pass
            elif next_date.date() == booking_date.date():
                if lab_tomorrow_time:
                    if start_hour >= float(lab_tomorrow_time):
                        will_lab_data_append = True
                    else:
                        pass
                else:
                    will_lab_data_append = True

            else:
                will_lab_data_append = True

            if will_lab_data_append:
                data_list = {"value": start_hour, "text": start_hour_text, "price": price, "is_available": is_available, "on_call": on_call}

        time_type = self.time_division.index(self.get_day_slot(start_hour))
        if not timing_date_obj[time_type].get('timing'):
            timing_date_obj[time_type]['timing'] = list()

        timing_date_obj[time_type]['timing'].append(data_list) if data_list else None;

    def get_key_or_field_value(self, obj, key, default_value=None):
        if hasattr(obj, key):
            return getattr(obj, key)
        else:
            if type(obj) is dict and obj.get(key):
                return obj[key]
            else:
                return default_value

def consumers_balance_refund():
    from keel.account.models import ConsumerAccount, ConsumerRefund
    refund_time = timezone.now() - timezone.timedelta(hours=settings.REFUND_INACTIVE_TIME)
    consumer_accounts = ConsumerAccount.objects.filter(updated_at__lt=refund_time, balance__gt=Decimal('0'))
    for account in consumer_accounts:
        with transaction.atomic():
            consumer_account = ConsumerAccount.objects.select_for_update().filter(pk=account.id).first()
            if consumer_account:
                if consumer_account.balance > 0:
                    print("consumer account balance " + str(consumer_account.balance))
                    ctx_objs = consumer_account.debit_refund()
                    if ctx_objs:
                        for ctx_obj in ctx_objs:
                            ConsumerRefund.initiate_refund(ctx_obj.user, ctx_obj)


class GenericAdminEntity():
    DOCTOR = 1
    HOSPITAL = 2
    LAB = 3
    EntityChoices = [(DOCTOR, 'Doctor'), (HOSPITAL, 'Hospital'), (LAB, 'Lab')]


def get_opd_pem_queryset(user, model):

    # super_user_query = '''CASE WHEN ((SELECT COUNT(id) FROM generic_admin WHERE user_id=%s AND hospital_id=hospital.id AND
    #                                   super_user_permission=true AND is_disabled=false) > 0) THEN 1  ELSE 0 END'''
    # appoint_query = '''CASE WHEN ((SELECT COUNT(id) FROM generic_admin WHERE user_id=%s AND hospital_id=hospital.id AND
    #                              super_user_permission=false AND is_disabled=false AND permission_type=1) > 0) THEN 1  ELSE 0 END'''
    # billing_query = '''CASE WHEN ((SELECT COUNT(id) FROM generic_admin WHERE user_id=%s AND hospital_id=hospital.id AND
    #                                super_user_permission=false AND is_disabled=false AND permission_type=2) > 0) THEN 1  ELSE 0 END'''

    manageable_hosp_list = auth_models.GenericAdmin.objects.filter(is_disabled=False, user=user) \
                                                           .values_list('hospital', flat=True)
    queryset = model.objects \
        .select_related('doctor', 'hospital', 'user') \
        .prefetch_related('doctor__manageable_doctors', 'hospital__manageable_hospitals', 'doctor__images',
                          'doctor__qualifications', 'doctor__qualifications__qualification',
                          'doctor__qualifications__specialization', 'doctor__qualifications__college',
                          'doctor__doctorpracticespecializations', 'doctor__doctorpracticespecializations__specialization',
                          'doctor__doctor_number', 'doctor__doctor_number__hospital') \
        .filter(hospital_id__in=list(manageable_hosp_list))\
        .annotate(pem_type=Case(When(Q(hospital__manageable_hospitals__user=user) &
                               Q(hospital__manageable_hospitals__super_user_permission=True) &
                               Q(hospital__manageable_hospitals__is_disabled=False), then=Value(3)),
                          When(Q(hospital__manageable_hospitals__user=user) &
                               Q(hospital__manageable_hospitals__super_user_permission=False) &
                               Q(hospital__manageable_hospitals__permission_type=auth_models.GenericAdmin.BILLINNG) &
                               ~Q(hospital__manageable_hospitals__permission_type=auth_models.GenericAdmin.APPOINTMENT) &
                               Q(hospital__manageable_hospitals__is_disabled=False), then=Value(2)),
                          When(Q(hospital__manageable_hospitals__user=user) &
                               Q(hospital__manageable_hospitals__super_user_permission=False) &
                               Q(hospital__manageable_hospitals__permission_type=auth_models.GenericAdmin.BILLINNG) &
                               Q(hospital__manageable_hospitals__permission_type=auth_models.GenericAdmin.APPOINTMENT) &
                               Q(hospital__manageable_hospitals__is_disabled=False), then=Value(3)),
                          default=Value(1),
                          output_field=IntegerField()
                          )
              )
    # .extra(select={'super_user': super_user_query, 'appointment_pem': appoint_query, 'billing_pem': billing_query}, params=(user_id, user_id, user_id))
    return queryset


def offline_get_day_slot(time):
    am = 'AM'
    pm = 'PM'
    if time < 12:
        return am
    elif time < 16:
        return pm
    else:
        return pm


def form_dc_time(time, am_pm):
    day_time_hour = int(time)
    day_time_min = (time - day_time_hour) * 60

    if day_time_hour > 12:
        day_time_hour -= 12

    day_time_hour_str = str(int(day_time_hour))
    if int(day_time_hour) < 10:
        day_time_hour_str = '0' + str(int(day_time_hour))

    day_time_min_str = str(int(day_time_min))
    if int(day_time_min) < 10:
        day_time_min_str = '0' + str(int(day_time_min))

    time_str = day_time_hour_str + ":" + day_time_min_str + " " + am_pm

    return time_str


def offline_form_time_slots(data, timing, is_available=True, is_doctor=True):
    start = Decimal(str(data['start']))
    end = Decimal(str(data['end']))
    time_span = TimeSlotExtraction.TIME_SPAN
    day = data.get('day')

    float_span = (Decimal(time_span) / Decimal(60))
    if isinstance(timing[day], dict) and not timing[day].get('timing'):
        timing[day] = []
    temp_start = start
    while temp_start <= end:
        am_pm = offline_get_day_slot(temp_start)
        time_str = form_dc_time(temp_start, am_pm)
        timing[day].append({'text': time_str,
                                      'value': temp_start,
                                      'mrp': data['fees'],
                                      'deal_price':data['deal_price']}
                                     )
        price_available_obj = {"price": data['fees'], "is_available": is_available}
        if is_doctor:
            price_available_obj.update({
                "mrp": data.get('mrp'),
                "deal_price": data.get('deal_price')
            })
        # price_available[day][temp_start] = price_available_obj
        temp_start += float_span
    return timing

def create_payout_checksum(all_txn, product_id):
    from keel.account.models import Order

    # secret_key = client_key = ""
    # if product_id == Order.DOCTOR_PRODUCT_ID:
    #     secret_key = settings.PG_SECRET_KEY_P1
    #     client_key = settings.PG_CLIENT_KEY_P1
    # elif product_id == Order.LAB_PRODUCT_ID:
    #     secret_key = settings.PG_SECRET_KEY_P2
    #     client_key = settings.PG_CLIENT_KEY_P2

    # secret_key = settings.PG_SECRET_KEY_P2
    # client_key = settings.PG_CLIENT_KEY_P2

    secret_key = settings.PG_PAYOUT_SECRET_KEY
    client_key = settings.PG_PAYOUT_CLIENT_KEY

    all_txn = sorted(all_txn, key=lambda x : x["idx"])
    checksum = ""
    for txn in all_txn:
        curr = "{"
        for k in sorted(txn.keys()):
            if str(txn[k]) and txn[k] is not None and txn[k] is not "":
                curr = curr + k + '=' + str(txn[k]) + ';'
        curr = curr + "}"
        checksum += curr

    checksum = secret_key + "|[" + checksum + "]|" + client_key
    checksum_hash = hashlib.sha256(str(checksum).encode())
    checksum_hash = checksum_hash.hexdigest()
    #print("checksum string - " + str(checksum) + "checksum hash - " + str(checksum_hash))
    #logger.error("checksum string - " + str(checksum) + "checksum hash - " + str(checksum_hash))
    return checksum_hash

def html_to_pdf(html_body, filename):
    from django.core.files.uploadedfile import InMemoryUploadedFile
    file = None
    response = get_pdf_njs(html_body, filename)
    try:
        temp_pdf_file = TemporaryUploadedFile(filename, 'byte', 1000, 'utf-8')
        for block in response.iter_content(1024 * 8):
            if not block:
                break
            temp_pdf_file.write(block)
        temp_pdf_file.seek(0)
        temp_pdf_file.content_type = "application/pdf"
        file = InMemoryUploadedFile(temp_pdf_file, None, filename, temp_pdf_file.content_type, temp_pdf_file.tell(), None)
    except Exception as e:
        logger.error("Got error while creating PDF file :: {}.".format(e))
    # try:
    #     extra_args = {
    #         'virtual-time-budget': 6000
    #     }
    #     from django.core.files.uploadedfile import TemporaryUploadedFile
    #     temp_pdf_file = TemporaryUploadedFile(filename, 'byte', 1000, 'utf-8')
    #     file = open(temp_pdf_file.temporary_file_path())
    #     from hardcopy import bytestring_to_pdf
    #     bytestring_to_pdf(html_body.encode(), file, **extra_args)
    #     file.seek(0)
    #     file.flush()
    #     file.content_type = 'application/pdf'
    #     from django.core.files.uploadedfile import InMemoryUploadedFile
    #     file = InMemoryUploadedFile(temp_pdf_file, None, filename, 'application/pdf',
    #                                 temp_pdf_file.tell(), None)
    #
    # except Exception as e:
    #     logger.error("Got error while creating PDF file :: {}.".format(e))
    return file

def util_absolute_url(url):
    if bool(urlparse(url).netloc):
        return url
    else:
        return settings.BASE_URL + url


def util_file_name(filename):
    import os
    if filename:
        filename = os.path.basename(filename)
    return filename

def format_iso_date(date_str):
    date_field = date_str.find('T')
    if date_field:
        date_field = date_str[:date_field]
    return date_field

def datetime_to_formated_string(instance, time_format='%Y-%m-%d %H:%M:%S', to_zone = tz.gettz(settings.TIME_ZONE)):
    instance = instance.astimezone(to_zone)
    formated_date = datetime.datetime.strftime(instance, time_format)
    return formated_date

def payout_checksum(request_payload):

    secretkey = settings.PG_SECRET_KEY_P2
    accesskey = settings.PG_CLIENT_KEY_P2

    checksum = ""

    curr = ''

    keylist = sorted(request_payload)
    for k in keylist:
        if request_payload[k] is not None:
            curr = curr + k + '=' + str(request_payload[k]) + ';'

    checksum += curr

    checksum = accesskey + "|" + checksum + "|" + secretkey
    checksum_hash = hashlib.sha256(str(checksum).encode())
    checksum_hash = checksum_hash.hexdigest()
    return checksum_hash

def get_package_free_or_not_dict(request):
    from keel.subscription_plan.models import UserPlanMapping
    package_free_or_not_dict = defaultdict(bool)
    if request.user and request.user.is_authenticated:
        free_test_in_user_plan = UserPlanMapping.get_free_tests(request)
        for temp_user_plan_package in free_test_in_user_plan:
            package_free_or_not_dict[temp_user_plan_package] = True
    return package_free_or_not_dict


def update_physical_agreement_value(obj, value, time):
    obj.assoc_hospitals.all().update(physical_agreement_signed=value, physical_agreement_signed_at=time)


def update_physical_agreement_timestamp(obj):
    from keel.doctor.models import HospitalNetwork
    to_be_updated = False
    time_to_be_set = None
    if obj.physical_agreement_signed and not obj.physical_agreement_signed_at:
        time_to_be_set = timezone.now()
        to_be_updated = True
    elif not obj.physical_agreement_signed and obj.physical_agreement_signed_at:
        time_to_be_set = None
        to_be_updated = True
    if to_be_updated:
        obj.physical_agreement_signed_at = time_to_be_set
        if isinstance(obj, HospitalNetwork):
            update_physical_agreement_value(obj, obj.physical_agreement_signed, time_to_be_set)


def ipd_query_parameters(entity, req_params):
    params_dict = copy.deepcopy(req_params)
    params_dict["max_distance"] = None
    if entity.sublocality_latitude:
        params_dict["lat"] = entity.sublocality_latitude
        params_dict["max_distance"] = 5  # In KMs
    elif entity.locality_latitude:
        params_dict["lat"] = entity.locality_latitude
        params_dict["max_distance"] = 15  # In KMs
    if entity.sublocality_longitude:
        params_dict["long"] = entity.sublocality_longitude
    elif entity.locality_longitude:
        params_dict["long"] = entity.locality_longitude
    if entity.locality_value:
        params_dict['city'] = entity.locality_value
    return params_dict


class AES_encryption:

    BLOCK_SIZE = 16

    @staticmethod
    def pad(data):
        length = AES_encryption.BLOCK_SIZE - (len(data) % AES_encryption.BLOCK_SIZE)
        return data + chr(length) * length

    @staticmethod
    def unpad(data):
        return data[:-ord(data[-1])]

    @staticmethod
    def encrypt(message, passphrase):
        IV = Random.new().read(AES_encryption.BLOCK_SIZE)
        aes = AES.new(passphrase, AES.MODE_CBC, IV)
        return base64.b64encode(IV + aes.encrypt(AES_encryption.pad(message)))

    @staticmethod
    def decrypt(encrypted, passphrase):
        try:
            encrypted = base64.b64decode(encrypted)
            IV = encrypted[:AES_encryption.BLOCK_SIZE]
            aes = AES.new(passphrase, AES.MODE_CBC, IV)
            return aes.decrypt(encrypted[AES_encryption.BLOCK_SIZE:]).decode("utf-8"), None
        except Exception as e:
            logger.error("Error while decrypting - " + str(e))
            return None, e


def convert_datetime_str_to_iso_str(datetime_string_to_be_converted):
    try:
        from dateutil import parser
        datetime_obj = parser.parse(datetime_string_to_be_converted)
        datetime_str = datetime_obj.isoformat()
        if datetime_str.endswith('+00:00'):
            datetime_str = datetime_str[:-6] + 'Z'
        result = datetime_str
    except Exception as e:
        print(e)
        result = datetime_string_to_be_converted
    return result


def patient_details_name_phone_number_decrypt(patient_details, passphrase):
    name = patient_details.get('encrypted_name')
    phone_number = patient_details.get('encrypted_phone_number')
    if name:
        name, exception = AES_encryption.decrypt(name, passphrase)
        if exception:
            return exception
    if phone_number:
        phone_number, exception = AES_encryption.decrypt(phone_number, passphrase)
        if exception:
            return exception
    patient_details['encrypted_name'] = None
    patient_details['name'] = ''.join(e for e in name if e.isalnum() or e == ' ')
    patient_details['encrypted_phone_number'] = None
    patient_details['phone_number'] = ''.join(e for e in phone_number if e.isalnum())


def format_return_value(value):
    if value == 'null':
        return None

    return value


def rc_superuser_login(**kwargs):
    from keel.provider.models import RocketChatSuperUser
    rc_super_user_obj = kwargs.get('rc_super_user_obj') if kwargs.get('rc_super_user_obj') else None
    username = rc_super_user_obj.username if rc_super_user_obj else settings.ROCKETCHAT_SUPERUSER
    password = rc_super_user_obj.password if rc_super_user_obj else settings.ROCKETCHAT_PASSWORD
    response = requests.post(settings.ROCKETCHAT_SERVER + '/api/v1/login',
                             data={
                                 "user": username,
                                 "password": password
                             })
    if response.status_code != status.HTTP_200_OK or not response.ok:
        logger.error("Error in Rocket Chat Superuser Login API - " + response.text)
        return None
    else:
        data = json.loads(response._content.decode())['data']
        auth_token = data.get('authToken')
        auth_user_id = data.get('userId')
        if rc_super_user_obj:
            rc_super_user_obj.token = auth_token
            rc_super_user_obj.user_id = auth_user_id
            rc_super_user_obj.save()
        else:
            rc_super_user_obj = RocketChatSuperUser.objects.create(username=username, password=password, user_id=auth_user_id, token=auth_token)
        return rc_super_user_obj


def rc_user_create(auth_token, auth_user_id, name, **kwargs):
    random_unique_string = uuid.uuid4().hex
    username = random_unique_string[:10].upper()
    password = random_unique_string[-10:]
    email = username + "@docprime.com"
    rc_req_extras = kwargs.get("rc_req_extras", dict())
    user_create_response = requests.post(settings.ROCKETCHAT_SERVER + '/api/v1/users.create',
                                         headers={'X-Auth-Token': auth_token,
                                                  'X-User-Id': auth_user_id,
                                                  'Content-Type': 'application/json'},
                                         data=json.dumps({
                                             "name": name,
                                             "email": email,
                                             "password": password,
                                             "username": username,
                                             "customFields": rc_req_extras
                                         }))
    if user_create_response.status_code != status.HTTP_200_OK or not user_create_response.ok:
        logger.error("Error in Rocket Chat user create API - " + user_create_response.text)
        return None
    response_data_dict = json.loads(user_create_response._content.decode())
    return {"name": name,
            "username": username,
            "email": email,
            "password": password,
            "rc_req_extras": rc_req_extras,
            "response_data": response_data_dict
            }


def rc_user_login(auth_token, auth_user_id, username):
    user_login_response = requests.post(settings.ROCKETCHAT_SERVER + '/api/v1/users.createToken',
                                        headers={'X-Auth-Token': auth_token,
                                                 'X-User-Id': auth_user_id,
                                                 'Content-Type': 'application/json'},
                                        data=json.dumps({"username": username}))
    if user_login_response.status_code != status.HTTP_200_OK or not user_login_response.ok:
        logger.error("Error in Rocket Chat user Login API - " + user_login_response.text)
        return None
    response_data_dict = json.loads(user_login_response._content.decode())
    return response_data_dict


def rc_group_create(auth_token, auth_user_id, patient, rc_doctor):
    members = [patient.rc_user.username, rc_doctor.username]
    group_name = str(rc_doctor.doctor.id) + '_' + str(patient.id)
    group_create_response = requests.post(settings.ROCKETCHAT_SERVER + '/api/v1/groups.create',
                                          headers={'X-Auth-Token': auth_token,
                                                   'X-User-Id': auth_user_id,
                                                   'Content-Type': 'application/json'},
                                          data=json.dumps({"name": group_name, "members": members}))
    if group_create_response.status_code != status.HTTP_200_OK or not group_create_response.ok:
        logger.error("Error in Rocket Chat user Login API - " + group_create_response.text)
        return None
    response_data_dict = json.loads(group_create_response._content.decode())
    return response_data_dict


def is_valid_uuid(uuid_to_test):
    try:
        uuid_obj = uuid.UUID(str(uuid_to_test), version=4)
        return True
    except ValueError:
        return False


def get_existing_rc_group(rc_user_patient, rc_user_doc):
    patient_group_ids = set()
    doc_group_ids = set()
    patient = rc_user_patient.online_patient if rc_user_patient.online_patient else rc_user_patient.offline_patient
    for econsultation in patient.econsultations.all():
        if econsultation.rc_group:
            patient_group_ids.add(econsultation.rc_group)
    for econsultation in rc_user_doc.doctor.econsultations.all():
        if econsultation.rc_group:
            doc_group_ids.add(econsultation.rc_group)
    rc_group = (patient_group_ids & doc_group_ids)
    return (list(rc_group)[0] if rc_group else None)


def create_rc_user_and_login_token(auth_token, auth_user_id, patient=None, doctor=None):
    from keel.provider.models import RocketChatUsers
    if patient:
        name = patient.name
        user_type = auth_models.User.CONSUMER
    elif doctor:
        name = doctor.name
        user_type = auth_models.User.DOCTOR
    else:
        raise Exception('either patient or doctor is required for creating rc_user')
    rc_req_extras = {'user_type': user_type}
    created_user_dict = rc_user_create(auth_token, auth_user_id, name, rc_req_extras=rc_req_extras)
    if not created_user_dict:
        return None
    username = created_user_dict.get('username')
    login_token = rc_user_login(auth_token, auth_user_id, username)['data']['authToken']
    if not login_token:
        return None

    if user_type == auth_models.User.DOCTOR:
        created_user_dict['doctor'] = doctor
    elif is_valid_uuid(patient.id):
        created_user_dict['offline_patient'] = patient
    else:
        created_user_dict['online_patient'] = patient
    rocket_chat_user_obj = RocketChatUsers.objects.create(**created_user_dict, login_token=login_token,
                                                          user_type=user_type)
    return rocket_chat_user_obj


def rc_users(e_obj, patient, auth_token, auth_user_id):
    from keel.provider.models import RocketChatGroups
    doctor = e_obj.doctor
    if hasattr(patient, 'rc_user') and patient.rc_user:
        rc_user_patient = patient.rc_user
    else:
        rc_user_patient = create_rc_user_and_login_token(auth_token, auth_user_id, patient=patient)
        if not rc_user_patient:
            return False
    if hasattr(doctor, 'rc_user') and doctor.rc_user:
        rc_user_doc = doctor.rc_user
    else:
        rc_user_doc = create_rc_user_and_login_token(auth_token, auth_user_id, doctor=doctor)
        if not rc_user_doc:
            return False

    rc_group_obj = get_existing_rc_group(rc_user_patient, rc_user_doc)
    if not rc_group_obj:
        rc_group_obj = RocketChatGroups.create_group(auth_token, auth_user_id, patient, rc_user_doc)
        if not rc_group_obj:
            return False
    e_obj.rc_group = rc_group_obj
    return True


def is_valid_ckeditor_text(text):
    if text == "<p>&nbsp;</p>":
        return False
    return True


def log_requests_on():
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.INFO)
    requests_log.propagate = True
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    requests_log.addHandler(ch)


def common_package_category(self, request):
    from keel.diagnostic.models import LabTestCategory
    from keel.api.v1.procedure.serializers import CommonCategoriesSerializer

    need_to_hit_query = True

    if request.user and request.user.is_authenticated and not hasattr(request, 'agent') and request.user.active_insurance and request.user.active_insurance.insurance_plan and request.user.active_insurance.insurance_plan.plan_usages:
        if request.user.active_insurance.insurance_plan.plan_usages.get('package_disabled'):
            need_to_hit_query = False

    categories_serializer = None

    if need_to_hit_query:
        categories = LabTestCategory.objects.filter(is_live=True, is_package_category=True,
                                                    show_on_recommended_screen=True).order_by('-priority')[:15]

        categories_serializer = CommonCategoriesSerializer(categories, many=True, context={'request': request})

    return (categories_serializer.data)


class IsPGRequest(permissions.BasePermission):
    message = 'PG is allowed to perform action only.'

    def has_permission(self, request, view):
        if request.META.get('HTTP_PG_AUTHORIZATION') and request.META.get('HTTP_PG_AUTHORIZATION') == (base64.b64encode(settings.PG_AUTH_TOKEN.encode())).decode():
            return True
        return False




