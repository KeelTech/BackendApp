# Generated by Django 3.2.3 on 2022-06-09 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0067_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'CUSTOMER'), (2, 'RCIC'), (3, 'ACCOUNT_MANAGER'), (4, 'STAFF'), (5, 'STUDENT')], default=1, null=True, verbose_name='User Types'),
        ),
    ]
