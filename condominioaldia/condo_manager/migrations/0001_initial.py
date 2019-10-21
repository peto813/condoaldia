# Generated by Django 2.1.3 on 2019-01-22 05:57

import condo_manager.upload_paths
import condo_manager.validators
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id_number', models.CharField(max_length=100, unique=True, verbose_name='Fiscal Number')),
                ('mobile', models.CharField(blank=True, max_length=15, null=True)),
                ('office', models.CharField(blank=True, max_length=15, null=True)),
                ('other', models.CharField(blank=True, max_length=15, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Condo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, verbose_name='Condo name')),
                ('approved', models.NullBooleanField(choices=[(None, 'Not evaluated'), (True, 'Approved'), (False, 'Rejected')], default=None, verbose_name='Approved')),
                ('approval_date', models.DateTimeField(null=True, verbose_name='Approval date')),
                ('id_proof', models.ImageField(blank=True, default='', help_text='You must select a file', upload_to=condo_manager.upload_paths.upload_comprobante_rif, verbose_name='fiscal number image')),
                ('logo', models.ImageField(blank=True, null=True, upload_to=condo_manager.upload_paths.upload_logo_function)),
                ('terms_accepted', models.BooleanField(default=False, null=True, verbose_name='Terms')),
                ('active', models.BooleanField(default=True, help_text='Condominiums will be deactivated when percentage falls below 99.75')),
                ('state', models.CharField(blank=True, default='', max_length=40, null=True, verbose_name='state')),
                ('city', models.CharField(default='', max_length=40, null=True, verbose_name='municipality')),
                ('address', models.CharField(max_length=200, null=True, verbose_name='address')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Inmueble',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share', models.DecimalField(decimal_places=4, default=0, max_digits=7, validators=[condo_manager.validators.validate_postitive], verbose_name='percentage representation')),
                ('initial_balance', models.DecimalField(decimal_places=4, max_digits=50, verbose_name='initial balance')),
                ('board_position', models.CharField(blank=True, max_length=20, null=True, verbose_name='board position')),
                ('name', models.CharField(help_text='House number or name; apartment number, etc', max_length=20, verbose_name='Property name')),
                ('owned_since', models.DateTimeField(default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('condo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inmuebles', to='condo_manager.Condo', verbose_name='Condominium')),
            ],
            options={
                'verbose_name': 'Property',
                'verbose_name_plural': 'Properties',
                'ordering': ['share'],
            },
        ),
        migrations.CreateModel(
            name='Rentee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('since', models.DateTimeField(auto_now_add=True)),
                ('terms_accepted', models.BooleanField(default=False, null=True, verbose_name='Terms')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terms_accepted', models.BooleanField(default=False, null=True, verbose_name='Terms')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='inmueble',
            name='rentee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='condo_manager.Rentee', verbose_name='Rentee'),
        ),
        migrations.AddField(
            model_name='inmueble',
            name='resident',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inmuebles', to='condo_manager.Resident'),
        ),
        migrations.AddField(
            model_name='condo',
            name='residents',
            field=models.ManyToManyField(related_name='resident_condos', through='condo_manager.Inmueble', to='condo_manager.Resident'),
        ),
        migrations.AddField(
            model_name='condo',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterUniqueTogether(
            name='inmueble',
            unique_together={('condo', 'name')},
        ),
    ]