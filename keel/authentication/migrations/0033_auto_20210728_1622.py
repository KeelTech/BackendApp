# Generated by Django 3.2.3 on 2021-07-28 10:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0032_merge_20210727_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerqualifications',
            name='end_date',
            field=models.DateField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='customerprofile',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='customerqualifications',
            name='deleted_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name='CustomerWorkExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('start_date', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('end_date', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('job_type', models.CharField(blank=True, default=2, max_length=512, null=True)),
                ('designation', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('job_description', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('company_name', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('city', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('weekly_working_hours', models.DateField(blank=True, default=None, max_length=512, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_workexp', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
