# -*- coding: utf-8 -*-
from rest_framework import serializers
# from rest_auth.registration.serializers import RegisterSerializer
# from allauth.account.utils import setup_user_email
# from allauth.account.adapter import get_adapter
# from django.conf import settings
# from django.utils.translation import ugettext_lazy as _
# from django.contrib.auth import get_user_model
from bank_keeping.models import Account
# from rolepermissions.roles import assign_role

#User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
	class Meta:
		fields = '__all__'
		model  = Account

