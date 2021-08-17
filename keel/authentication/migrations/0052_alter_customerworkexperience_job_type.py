# Generated by Django 3.2.3 on 2021-08-17 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0051_auto_20210817_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerworkexperience',
            name='job_type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'PART_TIME'), (2, 'FULL_TIME')], default=2, null=True),
        ),
    ]
