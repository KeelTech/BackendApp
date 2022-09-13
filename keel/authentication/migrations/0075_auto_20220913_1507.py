# Generated by Django 3.2.3 on 2022-09-13 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0074_auto_20220912_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerprofile',
            name='any_previous_marriage',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='city_of_birth',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='email',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='customerprofile',
            name='first_language',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='customerprofilelabel',
            name='any_previous_marriage_label',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='customerprofilelabel',
            name='city_of_birth_label',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='customerprofilelabel',
            name='email_label',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='customerprofilelabel',
            name='first_language_label',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='customerspouseprofile',
            name='date_of_marriage',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customerspouseprofile',
            name='number_of_children',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customerspouseprofilelabel',
            name='date_of_marriage_label',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customerspouseprofilelabel',
            name='number_of_children_label',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
