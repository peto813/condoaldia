from rest_framework import permissions
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.permissions import available_perm_status
from condominioaldia.roles import Condo


class CondoOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		return has_role(request.user, [Condo])

	def has_object_permission(self, request, view, obj):
		return has_role(request.user, [Condo])


