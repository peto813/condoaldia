import os
from django.contrib import admin
from .models import User, Condo, Resident, Inmueble, Rentee
from .forms import CondoForm, ResidentForm, RenteeForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rolepermissions.roles import get_user_roles
from django.utils.translation import ugettext_lazy as _


# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    '''
    This class registers the User model with the app admin
    '''
    readonly_fields = ('get_role',)

    def get_role(self, user):
        return user.role
    get_role.short_description = _("role")
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'mobile',
        'get_role',
    )


@admin.register(Condo)
class CondoAdmin(admin.ModelAdmin):
    '''
    This class registers the Condo model with the app admin
    '''
    list_display = (
        'id', 'name', 'approved','id_proof','approval_date', 'id_number',
    )
    readonly_fields = (
        'approval_date', 'logo', 'terms_accepted', 'user', 'id_proof',
    )
    # fields = ('name','id_number','approved',
    # 'approval_date','active', 'id_proof','terms_accepted','logo',)
    form = CondoForm

    def name(self, condo):
        return condo.user.full_name

    def id_number(self, condo):
        return condo.user.id_number


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    '''
    This class registers the Inmueble model with the app admin
    '''
    list_display = ('name', 'share', 'condo', 'resident',)
    # def name(self, obj):
    # 	return obj.user.get_full_name() or obj.user.email


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    '''
    This class registers the Resident model with the app admin
    '''
    form = ResidentForm
    list_display = ('id', 'name',)
    readonly_fields = ('name',)

    def name(self, resident):
        return resident.user.full_name

    def properties(self, resident):
        pass


@admin.register(Rentee)
class RenteeAdmin(admin.ModelAdmin):
    '''
    This class registers the Rentee model with the app admin
    '''
    form = RenteeForm
    list_display = ('id',)
    # readonly_fields = ('name',)
