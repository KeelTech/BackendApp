# Generated by Django 3.2.3 on 2021-07-06 16:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('description', models.TextField(blank=True, default=None, null=True)),
                ('price', models.FloatField(blank=True, default=True, null=True)),
                ('currency', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('country_iso', models.CharField(blank=True, default=None, max_length=512, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendors',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default=None, max_length=512, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Services',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('description', models.TextField(blank=True, default=False, null=True)),
                ('price', models.FloatField(blank=True, default=None, null=True)),
                ('country_iso', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('fulfillment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='Vendors', to='plans.vendors', verbose_name='Vendor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]