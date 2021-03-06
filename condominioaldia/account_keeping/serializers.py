# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Account, Transaction, Invoice, Order
from condo_manager.serializers import BaseUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.utils.translation import ugettext_lazy as _
from currency_history.models import Currency

User = get_user_model()
#HyperlinkedModelSerializer
class CurrencySerializer(serializers.ModelSerializer):
	class Meta:
		model= Currency
		fields= '__all__'

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

class OrderSerializer(serializers.ModelSerializer):
	invoice_order = serializers.BooleanField(
		label=_('Mark order as invoiced?'),
		initial=False,
		required=False,
	)
	class Meta:
		fields ='__all__'
		model  = Order

	def create(self, validated_data, *args, **kwargs):
		invoice_order=validated_data.pop('invoice_order', None)
		instance =super().create(validated_data, *args, **kwargs)
		if invoice_order:
			instance.create_invoice()
		return instance

	def update(self, instance, validated_data):
		instance = super().update(instance, *args, **kwargs)
		invoice_order=validated_data.pop('invoice_order', None)
		if invoice_order:
			instance.create_invoice()
		return instance

class TransactionSerializer(serializers.ModelSerializer):

	mark_invoice = serializers.BooleanField(
		label=_('Mark invoice as paid?'),
		initial=False,
		required=False,
	)
	billing_choices= (
		('ba', _('bill all')),
		('bl', _('bill listed')),
	)

	bill_mode = serializers.ChoiceField(choices= billing_choices, allow_blank = True, required = False)

	class Meta:
		fields ='__all__'
		model  = Transaction
		read_only_fields = ['account','value_net', 'value_gross']

	def validate(self, vd):
		bill_mode= vd.pop('bill_mode', None)
		if vd.get('transaction_type') =='w' and not bill_mode:
			raise serializers.ValidationError(_('Please state billing mode.'))
		if bill_mode:
			if bill_mode=='bl' and not vd.get('bill_list'):
				raise serializers.ValidationError(_('You must provide a list of properties to be billed.'))
		return vd

	def create(self, vd):
		mark_invoice=vd.pop('mark_invoice', None)
		request= self.context.get('request')
		
		instance= Transaction.objects.create(**vd)
		if hasattr(instance, 'invoice'):
			if instance.invoice and mark_invoice:
				# Set the payment date on related invoice
				instance.invoice.payment_date = instance.transaction_date
				instance.invoice.is_payed = mark_invoice
				instance.invoice.save()

		bill_mode=vd.pop('bill_mode', None)

		if bill_mode and transaction_type=='w':
			condo = request.user.condo
			if bill_mode=='ba':
				condo.bill_property(instance)
			elif bill_mode=='bl':
				raise NotImplementedError
				bill_list = vd.pop('bill_list')
				condo.bill_property(instance, bill_list)
		return instance

class InvoiceSerializer(serializers.ModelSerializer):
	condo = serializers.PrimaryKeyRelatedField( read_only= True)
	order= serializers.PrimaryKeyRelatedField(queryset = Order.objects.all())
	class Meta:
		fields ='__all__'
		model  = Invoice
		read_only_fields = ['account','value_net', 'value_gross']

	def update(self, invoice, validated_data):
		invoice.is_payed = validated_data.get('is_payed', invoice.is_payed)
		invoice.invoice_type = validated_data.get('invoice_type', invoice.invoice_type)
		invoice.save()
		return invoice