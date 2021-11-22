from django.test import TestCase
from keel.notifications.models import InAppNotification


class InAppNotificationModelTest(TestCase):

    def test_notification_create(self):
        notification = InAppNotification.objects.create(
            text='Test notification',
            user_id=1,
            case_id=1,
            category='test',
            seen = False
        )
        self.assertEqual(notification.text, 'Test notification')