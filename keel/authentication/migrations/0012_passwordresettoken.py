# Generated by Django 3.2.3 on 2021-06-29 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_merge_20210624_2147'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reset_token', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='password_reset_user_id', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'password_reset_token',
            },
        ),
    ]
