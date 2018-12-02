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
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
	#username = None
	password1 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	password2 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	id_number = serializers.CharField()
	id_proof = serializers.ImageField(required= True)
	terms = serializers.BooleanField(required= True)
	def validate_terms(self, terms):
		if not terms:
			raise serializers.ValidationError(_('You must accepd terms and conditions.'))
		return terms
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
		user.save()
		self.cleaned_data = self.get_cleaned_data()
		adapter.save_user(request, user, self)
		condominio = Condo(user= user, id_proof= self.validated_data.get('id_proof'))
		condominio.save()
		assign_role(user, 'condo')
		self.custom_signup(request, user)
		setup_user_email(request, user, [])
		return user

# class CustomUserDetailsSerializer(serializers.Serializer):
# 	email = serializers.EmailField(read_only= True)
# 	first_name =serializers.CharField()
# 	last_name =serializers.CharField()

class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
	#condo = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:condo-detail')
	class Meta:
		fields = [
			'first_name',
			'last_name',
			'email',
			'id_number',
			'date_joined',
			'last_login',
			'mobile',
			'office',
			'other',
			'city',
			'state',
			'address',
			'country',
			'condo'
		]
		model  = User
		# extra_kwargs = {
		# 	'url': {'view_name': 'condo_manager:user-detail'}
		# }



class BaseUserSerializer(serializers.ModelSerializer):
	country = CountryField()
	class Meta:
		#exclude =['id']
		model  = User
		extra_kwargs = {
			'password': {'write_only': True},
			#'url': {'view_name': 'rest_framew:user-details-view', 'lookup_field': 'pk'},
		}

class CondoSerializer(serializers.ModelSerializer):
	user = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:user-detail')
	class Meta:
		fields = '__all__'
		model  = Condo

class BaseInmuebleSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		read_only_fields=('owned_since',)
		model  = Inmueble

class InmuebleSerializer(BaseInmuebleSerializer):
	pass

class ResidentInmuebleSerializer(BaseInmuebleSerializer):
	class Meta(BaseInmuebleSerializer.Meta):
		read_only_fields= ['board_position', 'board_member']

class ResidentUserSerializer(BaseUserSerializer):
	class Meta(BaseUserSerializer.Meta):
		fields= ['email', 'first_name', 'last_name']

class ResidentSerializer(serializers.ModelSerializer):
	user = ResidentUserSerializer()
	inmueble =  serializers.PrimaryKeyRelatedField(queryset=Inmueble.objects.all(), write_only= True)
	class Meta:
		fields = ['user', 'inmueble']
		model  = Resident

	def create(self,vd, *args, **kwargs):
		request= self.context.get("request")
		user_data = vd.pop('user')
		inmueble = vd.pop('inmueble')
		user, created = User.objects.get_or_create(email = user_data.get('email'))
		if created:
			user.first_name= user_data.get('first_name' or None)
			user.last_name= user_data.get('last_name' or None)
			user.set_unusable_password()
			user.save()
			user.inmueble_instance=inmueble
			resident = Resident(user= user,**vd)
			resident.request= request
			resident.save()
			inmueble.resident = resident
			inmueble.save()
			return resident
		return user.resident
