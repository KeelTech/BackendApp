# Generated by Django 3.2.3 on 2021-10-16 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_auto_20211016_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='refund_amount_left',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=12, null=True),
        ),
    ]
