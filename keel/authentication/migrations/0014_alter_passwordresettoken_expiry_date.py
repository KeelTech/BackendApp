# Generated by Django 3.2.3 on 2021-07-01 12:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_auto_20210630_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 2, 18, 26, 31, 498902)),
        ),
    ]
