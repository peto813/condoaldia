# Generated by Django 2.1.3 on 2018-12-03 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0008_remove_inmueble_rented'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inmueble',
            name='board_member',
        ),
    ]
