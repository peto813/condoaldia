import os
from django.contrib import admin
from condo_manager.models import User, Condo, Resident, Inmueble
from condo_manager.forms import CondoForm 
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
from rolepermissions.roles import get_user_roles
from django.utils.translation import ugettext_lazy as _




@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields = ('get_role',)
    def get_role(self, user):
        return user.role
    get_role.short_description = _("role")
    list_display = ('id','username','email', 'first_name','last_name','mobile', 'get_role',)

@admin.register(Condo)
class CondoAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'approved','id_proof','approval_date','id_number',)
    readonly_fields = ('approval_date','logo', 'terms_accepted','user','id_proof',)
    #fields = ('name','id_number','approved','approval_date','active', 'id_proof','terms_accepted','logo',)
    form = CondoForm

    def name(self, condo):
    	return condo.user.full_name

    def id_number(self, condo):
    	return condo.user.id_number


@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    list_display = ('name', 'share','condo','resident',)
    # def name(self, obj):
    # 	return obj.user.get_full_name() or obj.user.email

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    readonly_fields = ('name',)

    def name(self, resident):
        return resident.user.full_name