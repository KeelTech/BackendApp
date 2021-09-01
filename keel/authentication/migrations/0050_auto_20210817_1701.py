# Generated by Django 3.2.3 on 2021-08-17 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0049_auto_20210816_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerqualifications',
            name='degree',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'BACHELORS'), (2, 'MASTERS')], default=1, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customerworkexperience',
            name='job_type',
            field=models.PositiveSmallIntegerField(blank=True, default=2, max_length=512, null=True),
        ),
    ]