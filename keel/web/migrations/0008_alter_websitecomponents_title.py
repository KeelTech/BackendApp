# Generated by Django 3.2.3 on 2022-05-30 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_alter_websitecomponents_blog_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='websitecomponents',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]