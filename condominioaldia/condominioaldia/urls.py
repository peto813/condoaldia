from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import ConfirmEmailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('condos/<int:condo_id>', include('condo_manager.urls')),
    path('condos/registration/', include('rest_auth.registration.urls')),
    path('condos/', include('rest_auth.urls')),
    path('condos/<int:condo_id>', include('account_keeping.urls'))
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
