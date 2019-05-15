from rest_framework import permissions
from condo_manager.models import Inmueble


class IsCondoOwnerOrReadOnly(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		#import pdb; pdb.set_trace()
		if request.user.is_condo:
			if request.user.condo == obj:
				return True
		elif request.user.is_resident:
			return Inmueble.objects.filter(condo= obj, resident = request.user.resident).exists() and request.method in permissions.SAFE_METHODS
		elif request.user.is_rentee:
			return Inmueble.objects.filter(condo= obj, rentee = request.user.rentee).exists() and request.method in permissions.SAFE_METHODS
		return False

class IsUserOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj == request.user or request.user.is_staff or request.user.is_superuser:
        	return True
        return False

class IsResidentAdminOrReadOnly(permissions.BasePermission):

	def has_permission(self, request, view):
		if request.user.is_condo:
			return True
		else:
			return request.method in permissions.SAFE_METHODS

	'''Used to set permissions in ResidentViewset endpoint'''
	def has_object_permission(self, request, view, obj):
		if request.user.is_resident and request.method in permissions.SAFE_METHODS and \
			obj==request.user.resident:
			return True
		elif request.user.is_condo:
			return Inmueble.objects.filter(condo= request.user.condo, resident = obj).exists()
		return False

class IsCondoAdminOrReadOnly(permissions.BasePermission):
	'''Used to set permissions in InmuebleViewset endpoint'''
	def has_permission(self, request, view):
		if request.user.is_condo:
			return True
		elif request.user.is_resident:
			return request.method in permissions.SAFE_METHODS


	def has_object_permission(self, request, view, obj):
		if request.user.is_condo and request.user.condo == obj.condo:
			return True
		else:
			return request.method in permissions.SAFE_METHODS and Inmueble.objects.filter(condo= obj.condo, resident = obj.resident).exists()