from django.db import models

# Create your models here.


class CurrencyMapping(models.Model):
    user_currency = models.CharField(max_length=128)
    stripe_currency = models.CharField(max_length=128)
    zero_decimal_currency = models.BooleanField(default=False)

    class Meta:
        db_table = "stripe_currency_mapping"
