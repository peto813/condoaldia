# Generated by Django 2.1.3 on 2019-01-22 05:45
import os

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db import connection, migrations

def load_data_from_sql(apps, schema_editor):
    BASE_DIR= settings.BASE_DIR
    file_path = os.path.join(BASE_DIR, 'account_keeping', 'custom_sql')
    file_path = os.path.join(os.path.dirname(__file__), '../custom_sql/', 'postgresql.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.execute(sql_statement)


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(load_data_from_sql)
    ]