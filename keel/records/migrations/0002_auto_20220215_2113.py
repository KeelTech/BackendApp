# Generated by Django 3.2.3 on 2022-02-15 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0015_plan_type'),
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesuser',
            name='case_type',
        ),
        migrations.AddField(
            model_name='salesuser',
            name='plan',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='plans.plan'),
        ),
    ]
