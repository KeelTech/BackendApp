# Generated by Django 3.2.3 on 2021-08-11 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0043_customerprofilelabel_phone_number_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificationlabel',
            name='grade_label',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]