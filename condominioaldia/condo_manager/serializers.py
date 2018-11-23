# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.utils import setup_user_email
from allauth.account.adapter import get_adapter
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Condo, Inmueble, Resident
from rolepermissions.roles import assign_role

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
	username = None
	password1 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	password2 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	id_number = serializers.CharField()
	id_proof = serializers.ImageField(required= True)

	def validate_id_proof(self, id_proof):
		content_type= id_proof.content_type.split('/')[1]
		if content_type not in settings.IMAGE_TYPES:
			raise serializers.ValidationError(_('File type is not supported'))
		file_size = id_proof.size
		limit_kb = 2500
		if file_size > limit_kb * 1024:
			raise serializers.ValidationError(_("Max size of file is %s KB" % limit_kb))
		return id_proof

	def save(self, request):
		adapter = get_adapter()
		user = adapter.new_user(request)
		user.id_number = self.validated_data.get('id_number')
		print(self.validated_data)
		print(self.validated_data.get('id_number' or None))
		user.save()
		self.cleaned_data = self.get_cleaned_data()
		adapter.save_user(request, user, self)
		condominio = Condo(user= user, id_proof= self.validated_data.get('id_proof'))
		condominio.save()
		assign_role(user, 'condo')
		self.custom_signup(request, user)
		setup_user_email(request, user, [])
		return user

class BaseUserSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		#fields= '_all_'
		model  = User
		extra_kwargs = {
			'password': {'write_only': True}
		}

class CondoSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		model  = Condo

class BaseInmuebleSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		model  = Inmueble

class InmuebleSerializer(BaseInmuebleSerializer):
	pass

class ResidentInmuebleSerializer(BaseInmuebleSerializer):
	class Meta(BaseInmuebleSerializer.Meta):
		#fields= None
		read_only_fields= ['board_position', 'board_member']

class ResidentUserSerializer(BaseUserSerializer):
	class Meta(BaseUserSerializer.Meta):
	# 	model  = User
		fields= ['email']

class ResidentSerializer(serializers.ModelSerializer):
	user= ResidentUserSerializer()
	#inmueble =  serializers.PrimaryKeyRelatedField(queryset=Inmueble.objects.all())
	inmueble=ResidentInmuebleSerializer()
	class Meta:
		fields = ['user', 'inmueble']
		model  = Resident
