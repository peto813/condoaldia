from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from rolepermissions.roles import get_user_roles
from condo_manager.upload_paths import *
from django.conf import settings
from django_countries.fields import CountryField
# Create your models here.


class User(AbstractUser):
	#location = models.CharField(max_length=250, null= True)
	#rif = models.CharField( max_length = 16, unique = True, blank = False, verbose_name = _('Fiscal number') )
	id_number = models.CharField(max_length=100, verbose_name=_('Fiscal Number'))
	mobile=models.CharField( null= True, blank = True, max_length=15)
	office=models.CharField( null= True, blank = True, max_length=15)
	other=models.CharField( null= True, blank = True, max_length=15)
	state = models.CharField( max_length = 40, null = True, default = '', blank = True,verbose_name = _('state' ))
	city = models.CharField( max_length = 40, null = True, default = '', blank = False, verbose_name = _('municipality') )
	address = models.CharField( max_length = 200, null = True, verbose_name = _('address') )
	country =  CountryField(null= True)

	#special=models.BooleanField(default= False)
	# class Meta:
	# 	verbose_name = _('user')
	# 	verbose_name_plural = _('users')
	# 	unique_together = ('email',)
	def __unicode__(self):
		return smart_unicode(self.nombre_inmueble )
		
	def get_full_name(self):
		'''
		Returns the first_name plus the last_name, with a space in between.
		'''
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()

	def get_short_name(self):
		'''
		Returns the short name for the user.
		'''
		return self.first_name

	def email_user(self, subject, message, from_email=None, **kwargs):
		'''
        Sends an email to this User.
		'''
		send_mail(subject, message, from_email, [self.email], **kwargs)

	@property
	def role(self):
		return get_user_roles(self)

class Resident(models.Model):
	user= models.OneToOneField(User, on_delete = models.CASCADE)


class Condo(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE, null = True, verbose_name = _('user'))
	residents = models.ManyToManyField(Resident, through = 'Inmueble', related_name='resident_condos')
	approved = models.NullBooleanField( default = None, verbose_name = _('Approved') )
	approval_date = models.DateTimeField( auto_now_add = True, auto_now = False, null = True, verbose_name = _('Approval date') )
	id_proof = models.ImageField( upload_to = upload_comprobante_rif, default='', null=False, blank= True, help_text=_('You must select a file'), verbose_name = _('fiscal number image'))
	logo = models.ImageField( upload_to = upload_logo_function, null = True, blank= True)
	terms_accepted = models.BooleanField(null = False, default = False, verbose_name = _('Terms'))
	active  = models.BooleanField(default = False, help_text =_("Condominiums will be deactivated when percentage falls below %s" %(settings.MINIMA_ALICUOTA)))
	#razon_rechazo = models.CharField(max_length=1000, blank = True, null = True, default = "", verbose_name = _('Rejection cause'))


class Inmueble(models.Model):
    share = models.DecimalField(max_digits=10, decimal_places=4, null = False, blank = True, default = 0, verbose_name = _('percentage representation'))
    rented = models.BooleanField(default = False, verbose_name = _('leased'))
    rentee = models.OneToOneField( User, on_delete = models.SET_NULL, null = True, verbose_name = _('Rentee') )
    initial_balance = models.DecimalField(max_digits=50, decimal_places=4, null = True, blank = True, default = 0, verbose_name = _('initial balance'))
    board_position = models.CharField( max_length=20, null= True, blank = True, verbose_name = _('board position') )
    condo = models.ForeignKey(Condo, null = True, on_delete= models.CASCADE, verbose_name = _('Condominium'), related_name='condo_inmuebles')
    balance = models.DecimalField(max_digits=25, decimal_places=4, null = False, blank = False, default = 0, verbose_name = _('current debt'))
    resident = models.ForeignKey(Resident, null = True, related_name = 'resident_inmuebles', on_delete = models.SET_NULL,)
    name = models.CharField(max_length=20, verbose_name=_('Property name'), null= True, help_text = 'House number or name; apartment number, etc')   
    board_member = models.BooleanField( default = False, verbose_name = _('board member') )
    #objects = InmuebleManager()
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name = _('Created'))
    
 #    class Meta:
 #        ordering = ['alicuota']

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