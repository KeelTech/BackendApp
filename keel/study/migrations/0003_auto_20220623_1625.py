# Generated by Django 3.2.3 on 2022-06-23 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_customerprofilelabel_qualificationlabel'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CustomerProfileLabel',
            new_name='StudentProfileLabel',
        ),
        migrations.RenameModel(
            old_name='QualificationLabel',
            new_name='StudentQualificationLabel',
        ),
    ]
