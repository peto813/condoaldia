from django.urls import path, re_path
from condo_manager import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from allauth.account.views import ConfirmEmailView


app_name="condo_manager"
router = DefaultRouter()
router.register(r'inmuebles', views.InmuebleViewSet)
router.register(r'residents', views.ResidentViewSet)
router.register(r'user', views.UserViewSet)#user-detail
router.register(r'condo_admin', views.CondoViewSet)

urlpatterns = [
	re_path(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/', views.CustomConfirmEmailView.as_view(), name='confirm-email'),
	#path('<int:condo_id>/', views.CondoViewSet.as_view({'get': 'retrieve'}), name= 'condo_details'),
    path('', include(router.urls))
]
