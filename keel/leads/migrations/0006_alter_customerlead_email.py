# Generated by Django 3.2.3 on 2021-05-30 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0005_alter_customerlead_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerlead',
            name='email',
            field=models.EmailField(default=None, max_length=254, null=True, verbose_name='Email'),
        ),
    ]
