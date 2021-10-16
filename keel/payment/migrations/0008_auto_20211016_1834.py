# Generated by Django 3.2.3 on 2021-10-16 13:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0011_merge_0010_alter_case_agent_0010_program_category'),
        ('payment', '0007_alter_casepaymentprofile_entity_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundAmountTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('payment_client_type', models.PositiveSmallIntegerField(choices=[(1, 'Stripe')], default=1)),
                ('webhook_payment_clients_identifier', models.CharField(max_length=1024, null=True, unique=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Cancelled'), (4, 'Initiated')], default=1)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='casepaymentprofile',
            name='currency',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='refund_amount_left',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=12),
        ),
        migrations.CreateModel(
            name='RefundTransaction',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('refund_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Initiated'), (3, 'Partial Initiated'), (4, 'Completed'), (5, 'Partial Completed'), (6, 'Cancelled')], default=1)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cases.case')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='customer_refund_transaction', to=settings.AUTH_USER_MODEL)),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='initiator_refund_transaction', to=settings.AUTH_USER_MODEL)),
                ('payment_transactions', models.ManyToManyField(to='payment.RefundAmountTransaction')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='refundamounttransaction',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='payment.transaction'),
        ),
    ]
