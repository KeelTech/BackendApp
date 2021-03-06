# Generated by Django 3.2.3 on 2021-07-12 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_alter_task_tags'),
        ('authentication', '0024_userservice'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocument',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tasks_docs', to='tasks.task'),
        ),
    ]
