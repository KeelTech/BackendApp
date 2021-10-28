from factory import Faker
from factory.django import DjangoModelFactory

from ..models import User


class UserFactory(DjangoModelFactory):
    username = Faker('text')
    phone_number = Faker('phone_number')
    email =Faker('internet')

    class Meta:
        model = User


