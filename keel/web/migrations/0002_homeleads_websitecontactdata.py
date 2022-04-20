# Generated by Django 3.2.3 on 2022-03-25 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeLeads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, default=None, max_length=20, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebsiteContactData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(blank=True, default=None, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('message', models.TextField(blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]