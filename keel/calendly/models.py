from django.db import models

from keel.Core.models import TimeStampedModel, SoftDeleteModel
from keel.authentication.models import User


class CalendlyUsers(TimeStampedModel, SoftDeleteModel):

    user = models.OneToOneField(User, on_delete=models.deletion.DO_NOTHING, related_name='calendly_details',
                                unique=True)
    user_resource_url = models.CharField(max_length=1024, null=True)
    event_type_resource_url = models.CharField(max_length=1024, null=True)

    class Meta:
        db_table = "calendly_user"
