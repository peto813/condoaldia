# Generated by Django 2.1.3 on 2018-11-17 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condo',
            name='approval_date',
            field=models.DateTimeField(null=True, verbose_name='Approval date'),
        ),
    ]