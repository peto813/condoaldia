# Generated by Django 2.1.3 on 2018-11-23 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0009_auto_20181123_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='inmueble',
            name='owned_since',
            field=models.DateTimeField(default=None),
        ),
    ]
