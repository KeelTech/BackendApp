from django.http import response
from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from keel.authentication.models import User


class CaseTests(APITestCase):

    def setUp(self):
        return super().setUp()
