from django.shortcuts import render
from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404
#from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
# Create your views here.
#from rest_framework.views import APIView
from condo_manager.models import Condo, Inmueble, Resident
from rest_framework.permissions import IsAuthenticated, AllowAny
from condo_manager.serializers import CondoSerializer, InmuebleSerializer, ResidentSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.views import ConfirmEmailView
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

class CreateListRetrieveViewSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, `create`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class RetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	pass

class CondoViewSet( RetrieveViewSet ):
	queryset= Condo.objects.all()
	serializer_class=CondoSerializer

	def retrieve(self, request, condo_id=None):
		condo = get_object_or_404(self.queryset, pk=condo_id)
		serializer = self.get_serializer(condo)
		return Response(serializer.data)


class InmuebleViewSet(CreateListRetrieveViewSet):
	queryset= Inmueble.objects.all()
	serializer_class= InmuebleSerializer
	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset().filter(condo = kwargs.get('condo_id')))
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

class ResidentViewSet(CreateListRetrieveViewSet):
	queryset= Resident.objects.all()
	serializer_class= ResidentSerializer

class CustomConfirmEmailView(ConfirmEmailView):
	template_name = "account/email_confirm." + app_settings.TEMPLATE_EXTENSION

	def post(self, *args, **kwargs):
		self.object = confirmation = self.get_object()
		confirmation.confirm(self.request)
		get_adapter(self.request).add_message(
			self.request,
			messages.SUCCESS,
			'account/messages/email_confirmed.txt',
			{'email': confirmation.email_address.email})
		if app_settings.LOGIN_ON_EMAIL_CONFIRMATION:
			resp = self.login_on_confirm(confirmation)
			if resp is not None:
				return res
		redirect_url = self.get_redirect_url()
		if not redirect_url:
			ctx = self.get_context_data()
			return self.render_to_response(ctx)
		return redirect(settings.LOGIN_URL)
