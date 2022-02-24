from django.conf import settings
from django.db import models
from django.utils import tree
from keel.cases.models import Case


class Notification(models.Model):
    # text = models.CharField(max_length=512, default=None, blank=True, null=True)
    text = models.JSONField(default=dict, blank=True, null=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, 
                                    default=None, blank=True, null=True)
    case_id = models.ForeignKey(Case, on_delete=models.DO_NOTHING, default=None, blank=True, null=True)
    category = models.CharField(max_length=32, default=None, blank=True, null=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class InAppNotification(Notification):
    pass

    def __str__(self):
        return str(self.pk)
