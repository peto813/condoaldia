from allauth.account.adapter import DefaultAccountAdapter
#from allauth.account.utils import send_email_confirmation
#emailaddress.send_confirmation()
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.template import TemplateDoesNotExist
from django.core.mail import EmailMessage, EmailMultiAlternatives

class CustomAccountAdapter(DefaultAccountAdapter):
	def send_confirmation_mail(self, request, emailconfirmation, signup=False):
		current_site = get_current_site(request)
		user= emailconfirmation.email_address.user
		activate_url = self.get_email_confirmation_url(request, emailconfirmation)
		ctx = {
			"user": user,
			"activate_url": activate_url,
			"current_site": current_site,
			"key": emailconfirmation.key,
			"full_name":user.full_name
		}
		if signup:
			ctx['signup']=True
			role_list= [item.get_name() for item in user.role]
			if 'condo' in role_list:
				email_template = 'account/email/email_confirmation'
			elif 'resident' in role_list:
				ctx['condo_name'] =user.inmueble_instance.condo.user.full_name
				ctx['resident_name']=user.full_name
				email_template = 'account/email/resident_email_confirmation_signup'
		else:
			email_template = 'account/email/email_confirmation'
		self.send_mail(email_template, emailconfirmation.email_address.email,ctx)
