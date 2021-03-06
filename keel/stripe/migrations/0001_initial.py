# Generated by Django 3.2.3 on 2021-09-06 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_currency', models.CharField(max_length=128)),
                ('stripe_currency', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'stripe_currency_mapping',
            },
        ),
    ]
