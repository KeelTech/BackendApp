# Generated by Django 3.2.3 on 2022-02-24 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_inappnotification_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='inappnotification',
            name='text_json',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
