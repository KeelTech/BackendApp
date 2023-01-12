# Generated by Django 3.2.3 on 2023-01-11 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0011_ieltsdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPostingData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.PositiveSmallIntegerField(choices=[(1, 'DESIGN'), (2, 'DEVELOPMENT'), (3, 'SALES'), (4, 'MARKETING'), (5, 'UI/UX')])),
                ('title', models.CharField(default=None, max_length=100)),
                ('location', models.PositiveSmallIntegerField(choices=[(1, 'Gurugram'), (2, 'Remote'), (3, 'Gurugram/Remote')])),
                ('experience', models.CharField(default=None, max_length=10)),
                ('skills', models.CharField(default=None, max_length=100)),
                ('description', models.CharField(default=None, max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
