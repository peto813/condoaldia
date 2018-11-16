from django.contrib import admin
from condo_manager.models import User, Condo, Resident
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
from rolepermissions.roles import get_user_roles
from django.utils.translation import ugettext_lazy as _

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields = ('get_role',)
    def get_role(self, user):
    	return get_user_roles(user)
    get_role.short_description = _("role")
    list_display = ('email', 'first_name','last_name','mobile', 'get_role',)


@admin.register(Condo)
class CondoAdmin(admin.ModelAdmin):
    list_display = ('name', 'approved','id_proof',)
    def name(self, obj):
    	return obj.user.get_full_name() or obj.user.email
