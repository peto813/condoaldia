import os, shutil
from django.utils import timezone
from django.dispatch import receiver
from .models import User, Condo, Inmueble, Resident
from django.db.models.signals import post_delete, pre_delete, post_save, pre_save
from rolepermissions.roles import assign_role
from allauth.account.utils import send_email_confirmation
# def send_condo_approve(condo):

# 	if condo.user.aprobado: # IF 'APROBADO' FIELD IS CHANGED TO APPROVED STATE
# 		site= Site.objects.get_current().domain
# 	    subject = loader.render_to_string('account/email/condo_approved_subject.txt', {})
# 	    message = loader.render_to_string('account/email/condo_approved_message.txt', {'name' : condo.user.first_name, 'site_name': site})
# 	    fromEmail = str(settings.DEFAULT_FROM_EMAIL)
# 	    emailList = [ condo.user.email ]
# 	    send_email.delay(subject, message, fromEmail, emailList, fail_silently = False )
# 	    condo.fecha_aprobacion = timezone.now()
# 	    obj.save()
# 	elif  not obj.aprobado:
# 	    razon_rechazo =  request.POST.get('razon_rechazo')
# 	    obj.razon_rechazo = str(razon_rechazo)
# 	    subject = _('Oops your condominium was not approved')
# 	    message = _('Dear '+obj.nombre+', we regret to inform you that your condominium was not approved. The reason is: '+ obj.razon_rechazo +'. You may try to register again!')
# 	    fromEmail = str(settings.DEFAULT_FROM_EMAIL)
# 	    emailList = [ condo.user.email ]     
# 	    send_email.delay(subject, message, fromEmail, emailList, fail_silently = False )
# 	    condo.user.delete()

@receiver(post_save, sender = Resident)
def post_resident_save(sender, instance, created,**kwargs):
	if created:
		'''
		in special cases the instance will be passed with a request attribute Eg;instance.resident by the
		serializer. Should be accounte for in the tests
		'''
		assign_role(instance.user, 'resident')#assigns role as resident
		if hasattr(instance, 'request'):
			send_email_confirmation(instance.request, instance.user, signup=True)

@receiver(post_delete, sender=Condo)
def post_condo_delete(sender, instance,**kwargs):
	'''
	DELETE THE USER AS WELL
	'''
	#DELETE COMPROBANTE RIF AND LOGO

	try:
		current_dir = os.path.dirname(instance.id_proof.path)
		parent= os.path.dirname(current_dir)
		shutil.rmtree(parent)
		#DELETE LOGO
		current_dir = os.path.dirname(instance.logo.path)
		parent= os.path.dirname(current_dir)
		shutil.rmtree(parent)
	except:
		pass
	user= instance.user
	user.delete()

@receiver(pre_save, sender=Condo)
def pre_condo_save(sender, instance,**kwargs):
	if instance.id:
		instance.previous_val = instance.__class__.objects.get(id=instance.id).approved


@receiver(post_save, sender=Condo)
def post_condo_save(sender, instance, created,**kwargs):
	#NEED TO SET THE APPROVED DATE
	if not created and instance.approved==True and instance.previous_val==None:
		instance.approve()

@receiver(pre_save, sender=Inmueble)
def pre_inmueble_save(sender, instance,**kwargs):
	if instance.id:
		instance.previous_val = instance.__class__.objects.get(id=instance.id).resident
		if instance.resident!= instance.previous_val:
			instance.resident_has_changed= True
			instance.owned_since = timezone.now()


@receiver(post_save, sender=Inmueble)
def post_inmueble_save(sender, instance, created,**kwargs):
	'''
	in special cases the instance will be passed with a request attribute Eg;instance.resident by the
	serializer. Should be accounte for in the tests
	'''
	if hasattr(instance, 'resident_has_changed') and instance.resident_has_changed and hasattr(instance.resident, 'request'):
		instance.resident.send_welcome_email(instance, instance.resident.request)
