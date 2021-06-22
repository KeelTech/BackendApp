from django.db import models
from keel.Core.models import TimeStampedModel


class CustomerLead(TimeStampedModel):
    WEB=1
    SALES=2
    SOCIAL=3
    LEAD_SOURCE_CHOICES = (
        (WEB, 'WEB'),
        (SALES, 'SALES'),
        (SOCIAL, 'SOCIAL')
    )
    INPROGRESS=1
    CONVERTED=2
    DROPPED=3
    RESOLUTION_CHOICES = (
        (INPROGRESS,'IN PROGRESS'),
        (CONVERTED, 'CONVERTED'),
        (DROPPED, 'DROPPED')
    )

    lead_source = models.PositiveSmallIntegerField(verbose_name="Lead Source", choices=LEAD_SOURCE_CHOICES)
    resolution = models.PositiveSmallIntegerField(verbose_name="Resolution", null=True, choices=RESOLUTION_CHOICES, default=INPROGRESS)
    name = models.CharField(verbose_name="Name", null=True, max_length=255)
    email = models.EmailField(verbose_name="Email", blank=False, null=True, default=None)
    phone_number = models.BigIntegerField(verbose_name='Phone Number', default=None, blank=False, null=True)
    is_active = models.BooleanField(verbose_name="Is Active", default=True)


    def __str__(self):
        return str(self.email)
    
    class Meta:
        db_table = "customer_lead"