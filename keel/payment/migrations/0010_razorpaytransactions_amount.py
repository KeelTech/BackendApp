# Generated by Django 3.2.3 on 2022-04-19 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20220419_0219'),
    ]

    operations = [
        migrations.AddField(
            model_name='razorpaytransactions',
            name='amount',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]