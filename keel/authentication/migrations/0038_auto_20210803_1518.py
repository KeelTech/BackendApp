# Generated by Django 3.2.3 on 2021-08-03 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0037_rename_institute_name_customerqualifications_institute'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkExperinceLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('user_label', models.CharField(default='user', max_length=255)),
                ('job_type_label', models.CharField(max_length=255)),
                ('designation_label', models.CharField(max_length=255)),
                ('job_description_label', models.CharField(max_length=255)),
                ('company_name_label', models.CharField(max_length=255)),
                ('city_label', models.CharField(max_length=255)),
                ('weekly_working_hours_label', models.CharField(max_length=255)),
                ('start_date_label', models.CharField(max_length=255)),
                ('end_date_label', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameModel(
            old_name='QualificationLabelModel',
            new_name='QualificationLabel',
        ),
    ]
