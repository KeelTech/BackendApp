# Generated by Django 3.2.3 on 2021-07-02 11:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_alter_passwordresettoken_expiry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 3, 11, 44, 58, 862542, tzinfo=utc)),
        ),
    ]
