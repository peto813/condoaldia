from django.shortcuts import render
from bank_keeping.models import Account
from bank_keeping.serializers import AccountSerializer
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
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

class AccountViewSet( CreateListRetrieveViewSet ):
	queryset= Account.objects.all()
	serializer_class=AccountSerializer
	permission_classes = (IsAuthenticated,)
	
	def get_queryset(self):
		obj  = self.queryset.first()
		return self.queryset.filter(user= self.request.user)
	# def retrieve(self, request, pk=None):
	# 	condo = get_object_or_404(self.queryset, pk=pk)
	# 	serializer = self.get_serializer(condo)
	# 	return Response(serializer.data)
