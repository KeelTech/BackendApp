# Generated by Django 3.2.3 on 2022-02-23 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0019_auto_20220107_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='index',
            field=models.IntegerField(default=0),
        ),
    ]
