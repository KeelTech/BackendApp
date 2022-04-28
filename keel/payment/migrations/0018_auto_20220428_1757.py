# Generated by Django 3.2.3 on 2022-04-28 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0017_auto_20220426_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='initiator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='initiator_order', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_items',
            field=models.ManyToManyField(blank=True, null=True, to='payment.OrderItem'),
        ),
    ]
