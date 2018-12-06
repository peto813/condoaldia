# Generated by Django 2.1.3 on 2018-12-02 23:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('condo_manager', '0004_auto_20181129_1933'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rentee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('since', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.AlterModelOptions(
            name='inmueble',
            options={'ordering': ['share'], 'verbose_name': 'Property', 'verbose_name_plural': 'Properties'},
        ),
        migrations.AlterField(
            model_name='inmueble',
            name='rentee',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='condo_manager.Rentee', verbose_name='Rentee'),
        ),
    ]