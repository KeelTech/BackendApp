# Generated by Django 3.2.3 on 2021-12-06 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0008_remove_triggeredemails_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triggeredemails',
            name='email',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
