from rest_framework import permissions
from rolepermissions.permissions import register_object_checker
from condominioaldia.roles import Condo, Resident

class IsCondoOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.user.is_condo:
			return True
		elif request.user.is_resident:
			'''
			ALLOW UNSAFE METHODS FOR RESIDENT IF POSTING FROM TRANSACTIONS
			'''
			if view.get_view_name()=='Transaction List':
				transaction_data = request.data
				if request.data['transaction_type']!='d':
					return False
				return True
		return request.method in permissions.SAFE_METHODS

	def has_object_permission(self, request, view, obj):
		if request.user.is_resident and request.method in permissions.SAFE_METHODS:
			if view.get_view_name()=='Transaction Instance':
				inmueble= request.user.resident.inmuebles.filter(resident= request.user.resident, condo = obj.account.user.condo).first()
				return request.user.resident.inmuebles.filter(resident= request.user.resident, condo = obj.account.user.condo).exists()
			return request.user.resident.inmuebles.filter(resident= request.user.resident, condo = obj.user.condo).exists()
		elif request.user.is_condo:
			if view.get_view_name()=='Transaction Instance':
				return request.user == obj.account.user
			return obj.user.condo == request.user.condo
		return False