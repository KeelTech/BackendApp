# Generated by Django 3.2.3 on 2021-10-07 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0063_user_call_default_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='relativeincanada',
            name='is_blood_relationship',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='relativeincanadalabel',
            name='is_blood_relationship_label',
            field=models.CharField(default=None, max_length=215, null=True),
        ),
    ]
