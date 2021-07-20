# Generated by Django 3.2.3 on 2021-07-20 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_case_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='account_manager_id',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='case',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'BOOKED'), (2, 'IN_PROGRESS'), (3, 'COMPLETED'), (4, 'CANCELLED')], default=1, verbose_name='case_status'),
        ),
    ]