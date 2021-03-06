from django.urls import path, re_path
from condo_manager import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from allauth.account.views import ConfirmEmailView

router = DefaultRouter()
router.register(r'properties', views.InmuebleViewSet)
router.register(r'residents', views.ResidentViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'condo_admin', views.CondoViewSet)
app_name="condo_manager"

urlpatterns = [
	re_path(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/', views.CustomConfirmEmailView.as_view(), name='confirm-email'),
    path('', include(router.urls)),
    
]
