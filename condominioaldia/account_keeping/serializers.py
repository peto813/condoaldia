# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Account, Transaction, Invoice
from condo_manager.serializers import BaseUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.translation import ugettext_lazy as _

User = get_user_model()
#HyperlinkedModelSerializer


# class CustomerHyperlink(serializers.HyperlinkedRelatedField):
# 	# We define these as class attributes, so we don't need to pass them as arguments.
# 	view_name = 'user-detail'
# 	queryset = User.objects.all()

# 	def get_url(self, obj, view_name, request, format):
# 		url_kwargs = {
# 			'organization_slug': obj.organization.slug,
# 			'customer_pk': obj.pk
# 		}
# 		return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

# 	def get_object(self, view_name, view_args, view_kwargs):
# 		lookup_kwargs = {
# 			'organization__slug': view_kwargs['organization_slug'],
# 			'pk': view_kwargs['customer_pk']
# 		}
# 		return self.get_queryset().get(**lookup_kwargs)


# class UserSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		#fields = ['user','name', 'account_number','routing_number','currency', 'initial_amount', 'total_amount', 'active']
# 		fields ='__all__'
# 		model  = User
# 		# extra_kwargs = {
# 		# 	'url': {'view_name': 'user-detail'}
# 		# 	#'users': {'view_name': 'rest_user_details'}
# 		# }


class AccountSerializer(serializers.ModelSerializer):
	# user=serializers.HyperlinkedIdentityField(
	# 	view_name='condo_manager:user-detail', read_only= True
	# )
	user = serializers.PrimaryKeyRelatedField( read_only= True)
	slug= serializers.SlugField(required= False)
	class Meta:
		fields ='__all__'
		model  = Account
		read_only_fields=['total_amount']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance!=None and getattr(self.instance, 'initial_amount', None)!=None:
			self.fields['initial_amount'].read_only = True

	def update(self, account, validated_data):
		account.active = validated_data.get('active', account.active)
		account.name = validated_data.get('name', account.active)
		account.save()
		return account

class TransactionSerializer(serializers.ModelSerializer):
	# user=serializers.HyperlinkedIdentityField(
	# 	view_name='user-detail', read_only= True
	# )
	#slug= serializers.SlugField(required= False)
	mark_invoice = serializers.BooleanField(
		label=_('Mark invoice as paid?'),
		initial=True,
		required=False
	)
	class Meta:
		#fields = ['user','name', 'account_number','routing_number','currency', 'initial_amount', 'total_amount', 'active']
		fields ='__all__'
		model  = Transaction
		read_only_fields = ['account']

	def save(self, *args, **kwargs):
		if hasattr(self.instance, 'invoice'):
			if self.instance.invoice and self.validated_data.get('mark_invoice'):
				# Set the payment date on related invoice
				self.instance.invoice.payment_date = self.instance.transaction_date
				self.instance.invoice.save()
		return super().save(*args, **kwargs)


class InvoiceSerializer(serializers.ModelSerializer):
	class Meta:
		fields ='__all__'
		model  = Invoice
