"""URLs to run the tests."""
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, re_path

#admin.autodiscover()
app_name = 'test_app'
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('account_keeping.urls')),
]
