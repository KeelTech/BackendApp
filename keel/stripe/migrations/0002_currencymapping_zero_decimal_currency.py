# Generated by Django 3.2.3 on 2021-09-17 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currencymapping',
            name='zero_decimal_currency',
            field=models.BooleanField(default=False),
        ),
    ]
