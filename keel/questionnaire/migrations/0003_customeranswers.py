# Generated by Django 3.2.3 on 2021-10-21 12:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0002_answer_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerAnswers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('answer', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='questionnaire.answer')),
                ('question', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='questionnaire.question')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
