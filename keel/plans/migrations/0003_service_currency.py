# Generated by Django 3.2.3 on 2021-07-22 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_auto_20210708_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='currency',
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
    ]
