# Generated by Django 3.2.3 on 2021-07-26 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0004_auto_20210723_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
