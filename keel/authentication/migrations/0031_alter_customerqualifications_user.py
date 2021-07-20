# Generated by Django 3.2.3 on 2021-07-20 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0030_alter_customerqualifications_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerqualifications',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_qualification', to=settings.AUTH_USER_MODEL),
        ),
    ]