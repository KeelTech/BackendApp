from faker import Factory
from factory.django import DjangoModelFactory

from ..models import User

faker = Factory.create()

class UserFactory(DjangoModelFactory):
    
    class Meta:
        model = User
    
    email = faker.email()
    phone_number = faker.phone_number()
