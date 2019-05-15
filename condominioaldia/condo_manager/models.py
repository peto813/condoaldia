import os, decimal, string, random, arrow
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from rolepermissions.roles import get_user_roles
from condo_manager.upload_paths import *
from django.conf import settings
from django_countries.fields import CountryField
from django.contrib.sites.models import Site
from django.template import loader
from django.core.mail import send_mail
from django.utils.encoding import smart_text
from django.core.exceptions import ValidationError
# Create your models here.
from django.db.models import Sum
from dateutil import relativedelta
#from allauth.account.utils import send_email_confirmation
from django.contrib.sites.shortcuts import get_current_site
from condo_manager.managers import UserManager, InmuebleManager
from condo_manager.validators import validate_postitive
from rolepermissions.checkers import has_permission, has_role
from condominioaldia.roles import Condo as CondoRole, Resident as ResidentRole, Rentee as RenteeRole

class User(AbstractUser):
	id_number = models.CharField(max_length=100, verbose_name=_('Fiscal Number'), unique= True, null = True, blank = True)
	mobile=models.CharField( null= True, blank = True, max_length=15)
	office=models.CharField( null= True, blank = True, max_length=15)
	other=models.CharField( null= True, blank = True, max_length=15)

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	@property
	def is_condo(self):
		if hasattr(self, 'condo') and self.condo!=None:
			return has_role(self, [CondoRole])
		return False

	@property
	def is_resident(self):
		if hasattr(self, 'resident') and self.resident!=None:
			return has_role(self, [ResidentRole])
		return False

	@property
	def is_rentee(self):
		return has_role(self, [RenteeRole])

	@property
	def full_name(self):
		'''
		Returns the first_name plus the last_name, with a space in between.
		'''
		full_name = '%s %s' % (self.first_name, self.last_name)
		if not self.first_name and not self.last_name:
			if hasattr(self, 'condo') and self.condo.name != None:
				full_name = self.condo.name
			else:
				full_name= self.email

		else:
			full_name= self.first_name + ' '+ self.last_name
		return full_name.strip().title()

	def get_short_name(self):
		'''
		Returns the short name for the user.
		'''
		return self.first_name

	def email_user(self, subject, message, from_email, to_email, fail_silently= False):
		'''
        Sends an email to this User.
		'''
		send_mail(subject, message, from_email, [self.email], fail_silently)

	@property
	def role(self):
		roles = []
		if self.is_condo:
			roles.append('condo')
		if self.is_rentee:
			roles.append('rentee')
		if self.is_resident:
			roles.append('resident')
		if self.is_superuser:
			roles.append('superuser')
		if self.is_staff:
			roles.append('staff')
		return roles

class Resident(models.Model):
	user= models.OneToOneField(User, on_delete = models.CASCADE)
	terms_accepted = models.BooleanField(null = True, default = False, verbose_name = _('Terms'))

	def send_welcome_email(self, inmueble):
		'''Email sent when a resident is related to a specific property'''
		current_site= Site.objects.get_current()
		#current_site = get_current_site(request)
		condo_name= inmueble.condo.user.full_name
		property_name= inmueble.name
		subject = loader.render_to_string('account/email/resident_welcome_subject.txt', {'condo_name':condo_name})
		message = loader.render_to_string('account/email/resident_welcome_message.txt', {'current_site': current_site, 'condo_name':condo_name, 'property_name':property_name, 'user':self.user,'full_name':self.user.full_name})
		fromEmail = str(settings.DEFAULT_FROM_EMAIL)
		emailList = [ self.user.email ]
		self.user.email_user(subject, message, fromEmail, emailList, fail_silently = False )

	def id_generator(self, size=6, chars=(string.ascii_uppercase + string.digits)):
		return ''.join(random.choice(chars) for _ in range(size))

	def assign_property(self, property):
		pass

	def remove_property(self, property):
		pass

	def __str__(self):
		return smart_text(self.user.full_name )

class Condo(models.Model):
	APPROVAL_CHOICES = (
		(None, _("Not evaluated")),
		(True, _("Approved")),
		(False, _("Rejected")),
	)
	name = models.CharField(max_length=25, blank = False, null = False, verbose_name = _('Condo name'))
	user = models.OneToOneField(User, on_delete = models.CASCADE, null = True, verbose_name = _('user'))
	residents = models.ManyToManyField(Resident, through = 'Inmueble', related_name='resident_condos')
	approved = models.NullBooleanField( default = None, verbose_name = _('Approved'), choices = APPROVAL_CHOICES )
	approval_date = models.DateTimeField(  null = True, verbose_name = _('Approval date') )
	id_proof = models.ImageField( upload_to = upload_comprobante_rif, default='', null=False, blank= True, help_text=_('You must select a file'), verbose_name = _('fiscal number image'))
	logo = models.ImageField( upload_to = upload_logo_function, null = True, blank= True)
	terms_accepted = models.BooleanField(null = True, default = False, verbose_name = _('Terms'))
	active  = models.BooleanField(default = True, help_text =_("Condominiums will be deactivated when percentage falls below %s" %(settings.MINIMA_ALICUOTA)))
	
	state = models.CharField( max_length = 40, null = True, default = '', blank = True,verbose_name = _('state' ))
	city = models.CharField( max_length = 40, null = True, default = '', blank = False, verbose_name = _('municipality') )
	address = models.CharField( max_length = 200, null = True, verbose_name = _('address') )
	country =  CountryField(null= False, blank = True)

	def get_current_billing_period(self):
		monthly_invoices = self.user.invoices.filter( invoice_type= 'm', user = self.user)
		if monthly_invoices.exists():
			next_monthly_invoice_date = arrow.get(monthly_invoices[0].invoice_date).ceil('month').replace(seconds=+1)
			billing_period= {
				'from': next_monthly_invoice_date.floor('month').datetime,
				'to':next_monthly_invoice_date.ceil('month').datetime
			}
		else:
			billing_period= {'from': arrow.get( self.user.date_joined).floor('month').datetime, 'to': arrow.get( self.user.date_joined).ceil('month').datetime}
		return billing_period


	def get_share_sum(self):
		total = self.inmuebles.all().aggregate(share= Sum('share'))['share'] or decimal.Decimal(0)
		return total

	def create_bank_account(self, data):
		from account_keeping.models import Account
		bank_account= Account.objects.create(user=self.user, **data)

	def approve(self):
		self.approval_date = timezone.now()
		self.save()
		self.send_condo_approved_email()

	def bill_property(self, transaction, bill_list = None):
		if self.get_share_sum()<0.995:
			raise ValidationError({'share': _('Total condo shares can not be less than 0.995 (99.5%%).')})
		from account_keeping.models import Order, OrderDetails
		transaction_amount = transaction.amount_net
		inmuebles = self.inmuebles.all()

		if bill_list:
			inmuebles = inmuebles.filter(pk__in=bill_list)
		
		for property in inmuebles:
			share = property.share
			share_amount = (share*transaction_amount) if not bill_list else (transaction_amount/inmuebles.count())
			order_data= {
				'condo':self,
				'order_type':'m',
				'customer':property.resident.user,
				'currency' :transaction.account.currency
			}
			order, created = Order.objects.get_or_create(**order_data)
			if created:
				order.order_date =transaction.transaction_date
				order.description =_('monthly bill orders')
				order.currency = transaction.account.currency
				order.save()

			order_detail = OrderDetails.objects.create(
				item_date= transaction.transaction_date,
				description =transaction.description,
				amount_gross = share_amount,
				order=order
			)
		return order



	# def create_monthly_bill(self):
	# 	from account_keeping.models import Transaction
	# 	period = self.get_current_billing_period()
	# 	#get all transactions
	# 	transactions = Transaction.objects.filter(account__user= self.user,
	# 		transaction_date__range=( period['from'], period['to']) )
	# 	#get properties
	# 	#print(dir(self))
	# 	#total_expenses = transaction.objects.filter(transaction_type='w').annotate(total_expenses=Sum('book__pages'))
	# 	for item in self.inmuebles.all():
	# 		print(item)

		#invoices = Invoice.objects.filter(user= self.user)

	def send_condo_approved_email(self):
		site= Site.objects.get_current().domain
		subject = loader.render_to_string('account/email/condo_approved_subject.txt', {})
		message = loader.render_to_string('account/email/condo_approved_message.txt', {'name' : self.user.full_name, 'site_name': site})
		fromEmail = str(settings.DEFAULT_FROM_EMAIL)
		emailList = [ self.user.email ]
		self.user.email_user(subject, message, fromEmail, emailList, fail_silently = False )
		#send_email.delay(subject, message, fromEmail, emailList, fail_silently = False )

	def __str__(self):
		return smart_text(self.user.full_name )


class Rentee(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, null = False, verbose_name = _('user'))
	since =models.DateTimeField(auto_now_add= True)
	terms_accepted = models.BooleanField(null = True, default = False, verbose_name = _('Terms'))



class Inmueble(models.Model):
	'''
	Inmueble is Property in spanish
	initial model was in spanish and name was kept for simplicity
	'''
	share = models.DecimalField(max_digits=7, decimal_places=4, null = False, blank = False, default = 0, validators= [validate_postitive],verbose_name = _('percentage representation'))
	rentee = models.ForeignKey( Rentee, on_delete = models.SET_NULL, null = True, verbose_name = _('Rentee') )
	initial_balance = models.DecimalField(max_digits=50, decimal_places=4, null = False, blank = False, verbose_name = _('initial balance'))
	board_position = models.CharField( max_length=20, null= True, blank = True, verbose_name = _('board position') )
	condo = models.ForeignKey(Condo, null = False, on_delete= models.CASCADE, verbose_name = _('Condominium'), related_name='inmuebles')
	resident = models.ForeignKey(Resident, null = True, related_name = 'inmuebles', on_delete = models.SET_NULL,)
	name = models.CharField(max_length=20, verbose_name=_('Property name'), null= False, help_text = 'House number or name; apartment number, etc')   
	owned_since = models.DateTimeField(default = None, null= True )
	created = models.DateTimeField(auto_now_add=True, null=True, verbose_name = _('Created'))
	
	def clean(self):
		share_sum = self.condo.get_share_sum()
		if share_sum + self.share>1:
			raise ValidationError({'share': _('Total condo shares can not be greater than 1 (100%%).')})
		
	@property
	def is_rented(self):
		if hasattr(self, 'board_position'):
			return self.rentee is not None
		return False

	@property
	def is_board_member(self):
		if hasattr(self, 'board_position'):
			return self.board_position is not None
		return False

	def get_balance(self, month=None):
		if not month:
			now = timezone.now()
			month = date(now.today().year, now.today().month, 1)
		next_month = month + relativedelta.relativedelta(months=1)

		'''
		the balance is the sum of ordinary payments minus unpaid invoices
		'''
		payments= Transaction.objects.all()
		# account_balance = self.transactions.filter(
		# 	parent__isnull=True,
		# 	transaction_date__lt=next_month,
		# ).aggregate(models.Sum('value_gross'))['value_gross__sum'] or 0
		# account_balance = account_balance + self.initial_amount
		# return account_balance
		return 0



	# def send_new_rentee_email(self):
	# 	site= Site.objects.get_current().domain
	# 	subject = loader.render_to_string('account/email/new_owner_email_subject.txt', {})
	# 	message = loader.render_to_string('account/email/new_owner_email_message.txt', {'name' : self.user.first_name, 'site_name': site})
	# 	fromEmail = str(settings.DEFAULT_FROM_EMAIL)
	# 	emailList = [ self.resident.user.email ]
	# 	self.resident.user.email_user(subject, message, fromEmail, emailList, fail_silently = False )

	# def send_new_resident_email(self):
	# 	site= Site.objects.get_current()
	# 	subject = loader.render_to_string('account/email/resident_email_confirmation_signup_subject.txt', {})
	# 	message = loader.render_to_string('account/email/resident_email_confirmation_signup_message.txt', {'name' : self.resident.user, 'site': site, 'user':self.resident.user, 'condo':self.condo})
		
	# 	fromEmail = str(settings.DEFAULT_FROM_EMAIL)
	# 	emailList = [ self.resident.user.email ]
	# 	#send_email_confirmation(request, user, signup=False)
	# 	self.resident.user.email_user(subject, message, fromEmail, emailList, fail_silently = False )
	# 	#send_email.delay(subject, message, fromEmail, emailList, fail_silently = False )
	# 	#self.fecha_aprobacion = timezone.now()
	# 	#send welcome email to new owner

	def change_rentee(self):
		pass

	def register_payment(self):
		pass

	class Meta:
		ordering = ['share']
		verbose_name =_('Property')
		verbose_name_plural = _('Properties')
		unique_together = (("condo", "name"),)
 #    @property
 #    def is_orphan(self):#TELLS IF INMUEBLE HAS OWNDER ATTACHED TO IT OR NOT
 #        if self.inquilino:
 #            return True
 #        else:
 #            return False
 #    @property
 #    def propietario(self):#TELLS IF INMUEBLE HAS OWNDER ATTACHED TO IT OR NOT
 #        try:
 #            return self.inquilino.user.get_full_name()
 #        except:
 #            pass
 #        return _("No owner assigned")

 #    def save(self, *args, **kwargs):
 #        self.nombre_inmueble = self.nombre_inmueble.strip().upper()
 #        if not self.factura_propietario_set.all().exists():
 #            self.deuda_actual=self.balanceinicial
 #        super(Inmueble, self).save(*args, **kwargs)
 #        condominio_activator( self.condominio)
        

 #    def delete(self, *args, **kwargs):
 #        condominio_activator(self.condominio)
 #        super(Inmueble, self).delete(*args, **kwargs)

	# def __unicode__(self):
	# 	return smart_unicode(self.nombre_inmueble )
	def __str__(self):
		return smart_text(self.name )