# Generated by Django 3.2.3 on 2021-06-26 17:03

from django.db import migrations, models
import keel.document.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('doc_pk', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('avatar', models.FileField(blank=True, upload_to=keel.document.utils.upload_files_to, verbose_name='Documents')),
                ('doc_type', models.SmallIntegerField(choices=[(0, 'Generic'), (1, 'Passport')], default=0)),
                ('owner_id', models.CharField(max_length=255)),
                ('original_name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
