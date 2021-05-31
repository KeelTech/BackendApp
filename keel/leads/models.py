from django.db import models
from keel.authentication.models import TimeStampedModel


class CustomerLead(TimeStampedModel):

    LEAD_SOURCE = (
        (1, 'WEB'),
        (2, 'SALES'),
        (3, 'SOCIAL')
    )

    RESOLUTION = (
        (1, 'CONVERTED'),
        (2, 'DROPPED')
    )

    lead_source = models.PositiveSmallIntegerField(verbose_name="Lead Source", choices=LEAD_SOURCE)
    resolution = models.PositiveSmallIntegerField(verbose_name="Resolution", null=True, choices=RESOLUTION)
    name = models.CharField(verbose_name="Name", null=True, max_length=255)
    email = models.EmailField(verbose_name="Email", blank=False, null=True, default=None)
    phone_number = models.BigIntegerField(verbose_name='Phone Number', default=None, blank=False, null=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)


    def __str__(self):
        return str(self.email)
    
    class Meta:
        db_table = "customer_lead"