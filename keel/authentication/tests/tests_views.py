from django.http import response
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from keel.authentication.models import User


class UserTests(APITestCase):

    def setUp(self):
        User.objects.create(email="usersetup@getkeel.com", password="testpass")

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('signup')
        data = {'email':'testuser@getkeel.com', 'password':'testpassword'}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        # self.assertEqual(User.objects.get().email, 'testuser@getkeel.com')
    
    # def 