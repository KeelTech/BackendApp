# Generated by Django 3.2.3 on 2021-09-23 10:28

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0012_alter_plan_check_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='check_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, default=list, size=None),
        ),
    ]