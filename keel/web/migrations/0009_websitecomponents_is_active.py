# Generated by Django 3.2.3 on 2022-05-31 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0008_alter_websitecomponents_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitecomponents',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]