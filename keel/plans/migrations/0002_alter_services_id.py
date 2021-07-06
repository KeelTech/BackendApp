# Generated by Django 3.2.3 on 2021-07-06 16:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='services',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
