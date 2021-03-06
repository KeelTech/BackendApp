# Generated by Django 3.2.3 on 2021-11-24 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0008_alter_question_answer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Text'), (2, 'Checkbox'), (3, 'Dropdown')], help_text='The answer type.'),
        ),
    ]
