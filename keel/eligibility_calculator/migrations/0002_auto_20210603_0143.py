# Generated by Django 3.2.3 on 2021-06-02 20:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eligibility_calculator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eligibilityresults',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='eligibilityresults',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
