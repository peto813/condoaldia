# Generated by Django 2.1.3 on 2018-11-20 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0004_auto_20181120_0730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmueble',
            name='initial_balance',
            field=models.DecimalField(decimal_places=4, max_digits=50, verbose_name='initial balance'),
        ),
    ]