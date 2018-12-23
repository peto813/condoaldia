"""URLs for the account_keeping app."""
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.conf.urls import url, include
from django.urls import path, re_path
from rest_framework_nested import routers
from . import views

app_name= "account_keeping"
#router = DefaultRouter()
router= routers.DefaultRouter()
router.register(r'', views.BankAccountsViewSet, basename="account"),
router.register(r'invoices', views.InvoiceViewSet, basename="invoice")
#router.register(r'user', views.UserViewSet)#user-detai




nested_router = routers.NestedDefaultRouter(router, r'', lookup='account')
nested_router.register(r'transactions', views.TransactionViewSet, base_name='transaction')

# 'base_name' is optional. Needed only if the same viewset is registered more than once
# Official DRF docs on this option: http://www.django-rest-framework.org/api-guide/routers/
urlpatterns = [
    
    url(r'transaction/(?P<pk>\d+)/$',
        views.TransactionUpdateView.as_view(),
        name='account_keeping_transaction_update'),

    path('transaction/create/',views.TransactionCreateView.as_view(),name='account_keeping_transaction_create'),

    # url(r'invoice/(?P<pk>\d+)/$',
    #     views.InvoiceUpdateView.as_view(),
    #     name='account_keeping_invoice_update'),

    # url(r'invoice/create/$',
    #     views.InvoiceCreateView.as_view(),
    #     name='account_keeping_invoice_create'),

    url(r'accounts/$',
        views.AccountListView.as_view(),
        name='account_keeping_accounts'),

    url(r'payees/(?P<pk>\d+)/$',
        views.PayeeUpdateView.as_view(),
        name='account_keeping_payee_update'),

    url(r'payees/create/$',
        views.PayeeCreateView.as_view(),
        name='account_keeping_payee_create'),

    url(r'payees/$',
        views.PayeeListView.as_view(),
        name='account_keeping_payees'),

    url(r'export/$',
        views.TransactionExportView.as_view(),
        name='account_keeping_export'),

    url(r'all/$',
        views.AllTimeView.as_view(),
        name='account_keeping_all'),

    url(r'(?P<year>\d+)/(?P<month>\d+)/$',
        views.MonthView.as_view(),
        name='account_keeping_month'),

    # url(r'(?P<year>\d+)/$',
    #     views.YearOverviewView.as_view(),
    #     name='account_keeping_year'),

    url(r'current-year/$',
        views.CurrentYearRedirectView.as_view(),
        name='account_keeping_current_year'),

    url(r'current-month/$',
        views.CurrentMonthRedirectView.as_view(),
        name='account_keeping_current_month'),

   # path('', views.BankAccountsViewSet.as_view({'get': 'list', 'post':'create'}), name='account_keeping_index'),
    path('', include(router.urls)),
    path('', include(nested_router.urls)),
    # url(r'',
    #     views.IndexView.as_view(),
    #     name='account_keeping_index'),
    

]
