from django.shortcuts import render
from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404
from condo_manager.models import Condo, Inmueble, Resident
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.views import ConfirmEmailView
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings
from rest_auth.registration.views import RegisterView
from allauth.account.utils import complete_signup
from rest_auth.app_settings import create_token
from allauth.account import app_settings as allauth_settings
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from django.contrib.auth import get_user_model
from condo_manager.serializers import  UserSerializer, CondoSerializer, InmuebleSerializer, ResidentSerializer
from condo_manager.permissions import *

User = get_user_model()

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

class CondoViewSet(  mixins.UpdateModelMixin, RetrieveViewSet):
	queryset= Condo.objects.all()
	serializer_class = CondoSerializer
	permission_classes=(IsAuthenticated, IsCondoOwnerOrReadOnly,)

class UserViewSet(mixins.UpdateModelMixin, RetrieveViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes=(IsAuthenticated, IsUserOwnerOrReadOnly,)

class InmuebleViewSet(CreateListRetrieveViewSet, mixins.UpdateModelMixin):
	queryset= Inmueble.objects.all()
	serializer_class= InmuebleSerializer
	permission_classes=(IsAuthenticated, IsCondoAdminOrReadOnly,)

	def get_queryset(self):
		user = self.request.user
		if user.is_condo:
			queryset= self.queryset.filter(condo=user.condo)
		elif user.is_resident:
			queryset= self.queryset.filter(resident=user.resident)
		return queryset

	def perform_create(self, serializer):
		instance = serializer.save(condo=self.request.user.condo)

class ResidentViewSet(CreateListRetrieveViewSet):
	queryset = Resident.objects.all()
	serializer_class = ResidentSerializer
	permission_classes=(IsAuthenticated, IsResidentAdminOrReadOnly,)

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

class GenerateMonthlyInvoiceView(APIView):
	permission_classes=(IsAuthenticated, IsCondoAdminOrReadOnly,)

	def post(self, request):
		pass