# Generated by Django 3.2.3 on 2021-05-27 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomerLeads',
            new_name='CustomerLead',
        ),
    ]
