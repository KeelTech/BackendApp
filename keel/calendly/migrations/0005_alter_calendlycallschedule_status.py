# Generated by Django 3.2.3 on 2021-12-07 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendly', '0004_alter_calendlycallschedule_invitee_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendlycallschedule',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Active'), (2, 'Rescheduled'), (3, 'Canceled'), (4, 'Completed')], default=1),
        ),
    ]
