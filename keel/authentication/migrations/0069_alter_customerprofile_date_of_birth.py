# Generated by Django 3.2.3 on 2022-08-02 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0068_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
