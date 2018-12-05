# Generated by Django 2.1.3 on 2018-12-03 16:19

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0006_auto_20181202_2322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='address',
        ),
        migrations.RemoveField(
            model_name='user',
            name='city',
        ),
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.RemoveField(
            model_name='user',
            name='state',
        ),
        migrations.AddField(
            model_name='condo',
            name='address',
            field=models.CharField(max_length=200, null=True, verbose_name='address'),
        ),
        migrations.AddField(
            model_name='condo',
            name='city',
            field=models.CharField(default='', max_length=40, null=True, verbose_name='municipality'),
        ),
        migrations.AddField(
            model_name='condo',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
        migrations.AddField(
            model_name='condo',
            name='state',
            field=models.CharField(blank=True, default='', max_length=40, null=True, verbose_name='state'),
        ),
    ]
