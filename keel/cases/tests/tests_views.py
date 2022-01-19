from django.http import response
from django.test.testcases import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from keel.authentication.models import User
from keel.cases.models import AgentNotes


class CaseTests(APITestCase):

    def setUp(self):
        return super().setUp()


class AgentNotesTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@email.com",
            password="test_password",
            user_type = User.RCIC)
        self.user.save()
    
    def test_create_agent_notes(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('create-agent-notes')
        data = {
            "notes": "test notes",
            "title": "test title"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AgentNotes.objects.count(), 1)
        self.assertEqual(AgentNotes.objects.get().notes, "test notes")