# Generated by Django 3.2.3 on 2022-05-27 07:30

import django.core.files.storage
from django.db import migrations, models
import keel.document.utils


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_websitecomponents'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitecomponents',
            name='blog_img',
            field=models.FileField(blank=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=keel.document.utils.upload_files_to, verbose_name='Blog Image'),
        ),
        migrations.AlterField(
            model_name='websitecomponents',
            name='component_name',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Contact Us'), (2, 'Home'), (3, 'Testimonials'), (4, 'Blog')], default=1),
        ),
    ]