from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import ConfirmEmailView
from django.conf.urls import (
handler400, handler403, handler404, handler500
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('condos/', include('condo_manager.urls')),
    path('condos/', include('rest_auth.urls')),
    path('condos/<int:condo_id>/', include('account_keeping.urls')),
    path('condos/registration/', include('rest_auth.registration.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#handler400 = 'my_app.views.bad_request'
#handler403 = 'my_app.views.permission_denied'
#handler404 = 'my_app.views.page_not_found'
#handler500 = 'my_app.views.server_error