# Generated by Django 3.2.3 on 2021-10-12 01:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0010_alter_case_agent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quotations', '0003_alter_quotation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotation',
            name='case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='case_quotations', to='cases.case'),
        ),
        migrations.AlterField(
            model_name='quotation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_quotations', to=settings.AUTH_USER_MODEL),
        ),
    ]
