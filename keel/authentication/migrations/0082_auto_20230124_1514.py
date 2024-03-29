# Generated by Django 3.2.3 on 2023-01-24 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0081_auto_20230113_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerfamilyinformation',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
        migrations.AddField(
            model_name='customerlanguagescore',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
        migrations.AddField(
            model_name='customerqualifications',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
        migrations.AddField(
            model_name='customerworkexperience',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
        migrations.AddField(
            model_name='educationalcreationalassessment',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
        migrations.AddField(
            model_name='relativeincanada',
            name='owner',
            field=models.CharField(blank=True, choices=[('self', 'SELF'), ('spouse', 'SPOUSE')], default='self', max_length=96, null=True),
        ),
    ]
