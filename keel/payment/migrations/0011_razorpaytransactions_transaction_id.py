# Generated by Django 3.2.3 on 2022-04-19 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_razorpaytransactions_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='razorpaytransactions',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
