# Generated by Django 3.2.3 on 2021-07-06 16:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0019_auto_20210706_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 6, 16, 10, 31, 846503, tzinfo=utc)),
        ),
    ]
