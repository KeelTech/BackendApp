from django.http import response
from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from keel.authentication.models import User


class UserTests(APITestCase):

    def setUp(self):
        self.credentials = {
            "email" : "usersetup@getkeel.com", 
            "password" : "testpass"
        }
        User.objects.create_user(**self.credentials)

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('signup')
        data = {'email':'testuser@getkeel.com', 'password':'testpassword'}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
    
    def test_without_password(self):
        """
        Ensure user cannot signup with password field not filled
        """
        url = reverse('signup')
        data = {'email':'testuser@getkeel.com', 'password':''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
    
    def test_invalid_email(self):
        """
        Ensure user cannot signup with invalid email
        """
        url = reverse('signup')
        data = {'email':'testuser', 'password':'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)


class UserLoginTest(APITestCase):
    def setUp(self):
        self.credentials = {
            "email" : "usersetup@getkeel.com", 
            "password" : "testpass"
        }
        User.objects.create_user(**self.credentials)
    
    def test_login_user(self):
        url = reverse('customer-login')
        response = self.client.post(url, self.credentials, format='json', follow=True)
        resp = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(resp['status'], 1)

    def test_login_user_invalid_credentials(self):
        url = reverse('customer-login')
        data = {'email':'wrong-user@getkeel.com', 'password':'wrong-password'}
        response = self.client.post(url, data, format='json', follow=True)
        resp = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
