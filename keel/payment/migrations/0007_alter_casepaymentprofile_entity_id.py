# Generated by Django 3.2.3 on 2021-10-12 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_alter_orderitem_item_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casepaymentprofile',
            name='entity_id',
            field=models.CharField(max_length=512),
        ),
    ]
