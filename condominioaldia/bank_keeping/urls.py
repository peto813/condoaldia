from django.urls import path, re_path
from bank_keeping import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
#from allauth.account.views import ConfirmEmailView

router = DefaultRouter()
router.register(r'banking', views.AccountViewSet, basename='inmuebles')

urlpatterns = [
    path('<int:condo_id>/', include(router.urls))
]
