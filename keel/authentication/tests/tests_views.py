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
