from faker import Factory, factory
import faker

from keel.notifications.models import InAppNotification

faker = Factory.create()


class InAppNotificationFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = InAppNotification

    user_id = faker.random_int(min=1, max=100)
    case_id = faker.random_int(min=1, max=100)
    text = faker.text()
    seen = False
