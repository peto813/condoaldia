import os, shutil
from django.dispatch import receiver
from .models import User, Condo
from django.db.models.signals import post_delete, pre_delete, post_save, pre_save

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

# @receiver(post_delete, sender=User)
# def post_user_delete(sender, instance, **kwargs):
# 	#DELETE COMPROBANTE RIF AND LOGO
# 	try:
# 		current_dir = os.path.dirname(instance.condo.id_proof.path)
# 		parent= os.path.dirname(current_dir)
# 		shutil.rmtree(parent)
# 		#DELETE LOGO
# 		current_dir = os.path.dirname(instance.condo.logo.path)
# 		parent= os.path.dirname(current_dir)
# 		shutil.rmtree(parent)
# 	except:
# 		pass

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
