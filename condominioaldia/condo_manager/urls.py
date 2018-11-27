from django.urls import path, re_path
from condo_manager import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from allauth.account.views import ConfirmEmailView

router = DefaultRouter()
router.register(r'inmuebles', views.InmuebleViewSet, basename='inmuebles')
router.register(r'residents', views.ResidentViewSet, basename='residents')

urlpatterns = [
	re_path(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/', views.CustomConfirmEmailView.as_view()),
	path('', views.CondoViewSet.as_view({'get': 'retrieve'})),
    #path('<int:condo_id>/residents/', views.ResidentRegisterView.as_view()),
    path('/', include(router.urls))
]
