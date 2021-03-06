# Generated by Django 3.2.3 on 2021-07-19 13:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0026_merge_20210714_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerQualifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('institute_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('grade', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('year_of_passing', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('start_date', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('city', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('country', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='qualification_user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('last_name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('mother_fullname', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('father_fullname', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('age', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('address', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('date_of_birth', models.DateField(default=None, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='general_user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
