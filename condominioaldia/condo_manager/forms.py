from condo_manager.models import Condo
from django import forms

class CondoForm(forms.ModelForm):
	name = forms.CharField()
	id_number = forms.CharField()


	def __init__(self, *args, **kwargs):
		instance = kwargs.get('instance' or None)
		if not kwargs.get('initial'):
			kwargs['initial'] = {}
		if instance:
			kwargs['initial'].update({'name': instance.user.get_full_name()})
			kwargs['initial'].update({'id_number': instance.user.id_number})
		super(CondoForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Condo
		fields = (
			'name',
			'id_number',
			'approved',
			'approval_date',
			'active',
			'id_proof',
			'terms_accepted',
			'logo',
		)


	def save(self, commit=True):
		data = self.cleaned_data
		condo = super(CondoForm, self).save(commit=False)
		id_number= data.get('id_number' or None)
		name= data.get('name' or None)
		condo.user.id_number= id_number
		condo.user.name	= name
		condo.user.save()
		if commit:
		    condo.save()
		return condo