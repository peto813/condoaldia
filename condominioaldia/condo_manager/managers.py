from django.db import models

class UserManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset()

class InmuebleManager(models.Manager):
	def get_queryset(self, user):
		role = user.role[0]
		return super().get_queryset()


