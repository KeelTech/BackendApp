# Generated by Django 3.2.3 on 2021-07-06 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='check_list',
            field=models.JSONField(default=dict, null=True),
        ),
    ]
