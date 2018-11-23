"""condominioaldia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import ConfirmEmailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    #re_path(r'^condos/registration/account-confirm-email/(?P<key>[-:\w]+)/', ConfirmEmailView.as_view()),
    path('accounts/', include('allauth.urls')),
    #http://localhost:8000/condos/registration/account-confirm-email/Nw:1gPNG5:tpc5mnOA9IRQikUeVjr4zbG7rUk/
    path('condos/', include('condo_manager.urls')),
    path('condos/registration/', include('rest_auth.registration.urls')),
    path('condos/', include('rest_auth.urls')),
    path('condos/', include('bank_keeping.urls')),
    
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


'''
Hello from example.com!

You're receiving this e-mail because user peto813 has given yours as an e-mail address to connect their account.

To confirm this is correct, go to http://localhost:8000/rest-auth/registration/account-confirm-email/MQ:1gNWvY:-faLYMbeEonne430ltsMDHHda9w/

Thank you from example.com!
example.com
'''