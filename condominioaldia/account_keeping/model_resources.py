from . import models
from import_export import resources
from import_export.fields import Field

class TransactionResource(resources.ModelResource):
    invoice_no = Field(column_name='Invoice No.')
    balance = Field(column_name='Balance')
    get_transaction_type = Field(column_name='Transaction type')

    @classmethod
    def field_from_django_field(self, field_name, django_field, readonly):
        field = resources.ModelResource.field_from_django_field(
            field_name, django_field, readonly)
        field.column_name = django_field.verbose_name
        return field

    class Meta:
        model = models.Transaction
        fields = ('id', 'transaction_date', 'description', 'invoice_no',
                  'payee__first_name', 'category__name', 'get_transaction_type',
                  'currency__iso_code', 'amount_net', 'vat', 'amount_gross',
                  'balance')
        export_order = fields

    def dehydrate_invoice_no(self, transaction):  # pragma: nocover
        if transaction.invoice_number:
            return transaction.invoice_number
        if transaction.invoice and transaction.invoice.invoice_number:
            return transaction.invoice.invoice_number
        return ''

    def dehydrate_balance(self, transaction):  # pragma: nocover
        account_balance = transaction.account.transactions.filter(
            models.Q(parent__isnull=True),
            models.Q(transaction_date__lt=transaction.transaction_date) |
            (models.Q(transaction_date=transaction.transaction_date,
                      pk__lte=transaction.pk)),
        ).aggregate(models.Sum('value_gross'))['value_gross__sum'] or 0
        return account_balance + transaction.account.initial_amount

    def dehydrate_get_transaction_type(self, transaction):  # pragma: nocover
        return transaction.get_transaction_type_display()
