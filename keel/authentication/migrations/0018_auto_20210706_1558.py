# Generated by Django 3.2.3 on 2021-07-06 10:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_alter_passwordresettoken_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'CUSTOMER'), (2, 'RCIC')], default=1, null=True, verbose_name='User Types'),
        ),
        migrations.AlterField(
            model_name='passwordresettoken',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 6, 10, 38, 16, 757563, tzinfo=utc)),
        ),
    ]
