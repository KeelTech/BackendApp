# Generated by Django 3.2.3 on 2022-08-03 19:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0071_auto_20220802_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerLanguageScoreLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('user_label', models.CharField(default='user', max_length=255)),
                ('test_type_label', models.CharField(max_length=255)),
                ('result_date_label', models.CharField(max_length=255)),
                ('test_version_label', models.CharField(max_length=255)),
                ('report_form_number_label', models.CharField(max_length=255)),
                ('listening_score_label', models.CharField(max_length=255)),
                ('writing_score_label', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('speaking_score_label', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('reading_score_label', models.CharField(max_length=255)),
                ('mother_tongue_label', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'language_scores_label',
            },
        ),
        migrations.CreateModel(
            name='CustomerLanguageScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('test_type', models.PositiveSmallIntegerField(choices=[(1, 'IELTS'), (2, 'CELPIP'), (3, 'PTE')])),
                ('result_date', models.DateField(blank=True, null=True)),
                ('test_version', models.CharField(blank=True, max_length=256, null=True)),
                ('report_form_number', models.CharField(blank=True, max_length=512, null=True)),
                ('listening_score', models.IntegerField()),
                ('writing_score', models.IntegerField()),
                ('speaking_score', models.IntegerField()),
                ('reading_score', models.IntegerField()),
                ('mother_tongue', models.CharField(blank=True, max_length=256, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_lang_score', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'customer_language_scores',
            },
        ),
    ]
