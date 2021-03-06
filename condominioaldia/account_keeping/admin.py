"""Admin classes for the account_keeping app."""
from django.contrib import admin

from . import models


class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'owner_name','id','name', 'slug', 'currency', 'initial_amount', 'total_amount']
    def owner_name(self, account):
        return account.user
    read_only_fields=['user']
admin.site.register(models.Account, AccountAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    pass
    # list_display = [
    #     'invoice_type', 'invoice_date', 'currency', 'amount_net', 'vat',
    #     'amount_gross', 'payment_date']
    # list_filter = ['invoice_type', 'currency', 'payment_date']
    # date_hierarchy = 'invoice_date'
    # search_fields = ['invoice_number', 'description']
admin.site.register(models.Invoice, InvoiceAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_type', 'order_date', 'currency', 'amount_net', 'vat',
        'amount_gross', 'payment_date']
    list_filter = ['order_type', 'currency', 'payment_date']
    date_hierarchy = 'order_date'
    search_fields = ['order_number', 'description']
admin.site.register(models.Order, OrderAdmin)

class PayeeAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Payee, PayeeAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Category, CategoryAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date', 'parent', 'invoice', 'payee',
        'category', 'value_net', 'vat', 'value_gross', ]
    list_filter = ['account', 'payee', 'category']
    date_hierarchy = 'transaction_date'
    raw_id_fields = ['parent', 'invoice']
    search_fields = ['invoice__invoice_number', 'description']
admin.site.register(models.Transaction, TransactionAdmin)
