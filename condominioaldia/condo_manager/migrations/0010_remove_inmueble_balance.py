# Generated by Django 2.1.3 on 2018-12-03 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0009_remove_inmueble_board_member'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inmueble',
            name='balance',
        ),
    ]
