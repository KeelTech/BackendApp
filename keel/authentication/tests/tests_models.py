from django.test import TestCase

from ..models import User
from .factories import UserFactory

class UserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = UserFactory._meta.model
    
    def test_crud_user(self):
        # create
        user = UserFactory(email="usertests@getkeel.com", 
                            password="newpassword",
                            phone_number="0987654321")

        # read
        self.assertEqual(user.email, 'usertests@getkeel.com')
        self.assertEqual(user.pk, user.id)