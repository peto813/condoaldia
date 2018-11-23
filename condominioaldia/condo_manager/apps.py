from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CondoManagerConfig(AppConfig):
	name = 'condo_manager'
	verbose_name = _('Condo manager')

	def ready(self):
		#to avoid circylar imports we perform them once app is initialized
		import condo_manager.signals  # noqa