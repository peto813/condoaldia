from condo_manager.models import Condo
from django import forms
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _

User = get_user_model()
class CondoForm(forms.ModelForm):
	name = forms.CharField(max_length=100)
	id_number = forms.CharField()
	country = CountryField(blank_label=_('select country')).formfield()
	address = forms.CharField(max_length=100)
	city= forms.CharField(max_length=25)
	state= forms.CharField(max_length=25)
	mobile = forms.CharField(max_length=15, required= False)
	office = forms.CharField(max_length=15, required= False)
	other  = forms.CharField(max_length=15, required= False)

	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance' or None)
		if not kwargs.get('initial'):
			kwargs['initial'] = {}
		if instance:
			kwargs['initial'].update({'name': instance.name})
			kwargs['initial'].update({'id_number': instance.user.id_number})
			kwargs['initial'].update({'address': instance.user.address})
			kwargs['initial'].update({'country': instance.user.country})
			kwargs['initial'].update({'city': instance.user.city})
			kwargs['initial'].update({'state': instance.user.state})
			kwargs['initial'].update({'mobile': instance.user.mobile})
			kwargs['initial'].update({'office': instance.user.office})
			kwargs['initial'].update({'other': instance.user.other})

		super(CondoForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Condo
		fields = (
			'name',
			'id_number',
			'country',
			'address',
			'city',
			'state',
			'approved',
			'approval_date',
			'id_proof',
			'terms_accepted',
			'logo',
			'active'
		)


	def save(self, commit=True):
		data = self.cleaned_data
		condo = super(CondoForm, self).save(commit=False)
		id_number= data.get('id_number' or None)
		name= data.get('name' or None)
		condo.user.id_number= id_number
		condo.user.country= data.get('country')
		condo.user.address= data.get('address')
		condo.user.state= data.get('state')
		condo.user.city=  data.get('city')
		condo.user.mobile=  data.get('mobile')
		condo.user.office=  data.get('office')
		condo.user.other=  data.get('other')
		condo.name	= name
		condo.user.save()
		if commit:
		    condo.save()
		return condo


class UserForm(forms.ModelForm):
	#name = forms.CharField()
	#id_number = forms.CharField()
	
	class Meta:
		model = User
		fields = '__all__'