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
from rest_auth.serializers import PasswordResetSerializer, TokenSerializer
from rest_auth.models import TokenModel
User = get_user_model()

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class CustomPwdResetSerializer(PasswordResetSerializer):

	def validate_email(self, value):
        # Create PasswordResetForm with the serializer
		email_exists = User.objects.filter(email = value).exists()
		if not email_exists:
			raise serializers.ValidationError(_("Invalid E-mail."))
		self.reset_form = self.password_reset_form_class(data=self.initial_data)
		if not self.reset_form.is_valid():
			raise serializers.ValidationError(self.reset_form.errors)
		return value




class CustomRegisterSerializer(RegisterSerializer):
	password1 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	password2 = serializers.CharField(style={'input_type': 'password'},write_only=True, min_length = 8, allow_blank=False, trim_whitespace=True)
	#id_number = serializers.CharField()
	id_proof = serializers.ImageField(required= True)
	terms = serializers.BooleanField(required= True)
	name = serializers.CharField()
	username =None
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
		#user.id_number = self.validated_data.get('id_number')
		user.save()
		self.cleaned_data = self.get_cleaned_data()
		adapter.save_user(request, user, self)
		vd =self.validated_data
		condominio = Condo(user= user,terms_accepted=vd.get('terms'), name= vd.get('name'), id_proof= vd.get('id_proof'))
		condominio.save()
		self.custom_signup(request, user)
		setup_user_email(request, user, [])
		return user


class UserSerializer(DynamicFieldsModelSerializer):
	#condo = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:condo-detail')
	#resident = None
	#rentee = None
	role = serializers.ListField(read_only= True)
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
			#'condo',
			#'resident',
			#'rentee',
			'role'
		]
		model  = User
		read_only_fields= ['last_login','date_joined']



class RenteeSerializer(serializers.Serializer):
    pass


class BaseUserSerializer(serializers.ModelSerializer):
	country = CountryField(country_dict=True)
	class Meta:
		model  = User
		extra_kwargs = {
			'password': {'write_only': True},
		}

class CondoSerializer(CountryFieldMixin, serializers.ModelSerializer):
	#user = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:user-detail')
	user = UserSerializer()
	class Meta:
		exclude = ['terms_accepted']
		model  = Condo
		read_only_fields=('active','approved', 'id','approval_date',)

class BaseInmuebleSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		read_only_fields=('owned_since',)
		model  = Inmueble

class InmuebleSerializer(BaseInmuebleSerializer):
	condo = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:condo-detail', lookup_field= 'pk')
	resident = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:resident-detail', lookup_field= 'pk')
	#renteegit = serializers.HyperlinkedIdentityField(view_name= 'condo_manager:resident-detail', lookup_field= 'pk')
	
	def validate(self, validated_data):
		request= self.context.get('request')
		validated_data['condo'] = request.user.condo
		instance = Inmueble(**validated_data)
		instance.clean()
		return validated_data


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

class customTokenSerializer(TokenSerializer):
	'''
	Serializer used when logging in, returns user data
	'''
	profile_serializers = {
		'condo': CondoSerializer,
		'resident' : ResidentSerializer,
		'rentee': RenteeSerializer
	}

	class Meta:
		fields= '__all__'
		model = TokenModel
	
	account = serializers.SerializerMethodField(read_only=True)

	def get_account(self, obj):
		profile_map = obj.user.get_profile_map()
		role = profile_map['role']
		profile_serializer = self.profile_serializers[role]
		return  profile_serializer(profile_map['profile']).data

