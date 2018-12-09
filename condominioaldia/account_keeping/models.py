"""
Models for the account_keeping app.

TODO: Add lazy_trans and docstrings

"""
from datetime import date
from decimal import Decimal

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from currency_history.models import Currency, CurrencyRateHistory
from dateutil import relativedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class AmountMixin(object):
    """
    Mixin that handles amount_net, vat and amount_gross fields on save().

    """
    def set_amount_fields(self):
        if self.amount_net and not self.amount_gross:
            if self.vat:
                self.amount_gross = \
                    self.amount_net * (self.vat / Decimal(100.0) + 1)
            else:
                self.amount_gross = self.amount_net

        if self.amount_gross and not self.amount_net:
            if self.vat:
                self.amount_net = \
                    Decimal(1.0) / (self.vat / Decimal(100.0) + 1) \
                    * self.amount_gross
            else:
                self.amount_net = self.amount_gross

    def set_value_fields(self, type_field_name):
        multiplier = 1
        type_ = getattr(self, type_field_name)
        if type_ == Transaction.TRANSACTION_TYPES['withdrawal']:
            multiplier = -1
        elif type_ == Transaction.TRANSACTION_TYPES['pending']:
            multiplier = 0
        self.value_net = self.amount_net * multiplier
        self.value_gross = self.amount_gross * multiplier


@python_2_unicode_compatible
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_accounts", null= True)
    account_number= models.CharField(max_length=25, null= False, blank= False)
    routing_number = models.CharField(max_length=25, null= True, blank= True)

    name = models.CharField(
        max_length=128,
        verbose_name=_('Name'),
        unique= True
    )

    slug = models.SlugField(
        max_length=128,
        verbose_name=_('Slug'),
    )

    currency = models.ForeignKey(
        'currency_history.Currency',
        related_name='accounts',
        verbose_name=_('Currency'),
        on_delete = models.PROTECT
    )

    initial_amount = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Initial amount'),
    )

    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Total amount'),
    )

    active = models.BooleanField(
        default=True,
        verbose_name=_('Active?'),
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def get_balance(self, month=None):
        """
        Returns the balance up until now or until the provided month.

        """
        if not month:
            month = date(date.today().year, date.today().month, 1)
        next_month = month + relativedelta.relativedelta(months=1)
        account_balance = self.transactions.filter(
            parent__isnull=True,
            transaction_date__lt=next_month,
        ).aggregate(models.Sum('value_gross'))['value_gross__sum'] or 0
        account_balance = account_balance + self.initial_amount
        return account_balance


class InvoiceManager(models.Manager):
    """Custom manager for the ``Invoice`` model."""
    def get_without_pdf(self):
        qs = Invoice.objects.filter(pdf='')
        qs = qs.prefetch_related('transactions', )
        return qs


@python_2_unicode_compatible
class Invoice(AmountMixin, models.Model):
    INVOICE_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
        'ordinary': 'o',
        'extra-ordinary': 'eo'
    }
    INVOICE_TYPE_CHOICES = [
        (INVOICE_TYPES['withdrawal'], 'withdrawal'),
        (INVOICE_TYPES['deposit'], 'deposit'),
        (INVOICE_TYPES['ordinary'], 'ordinary'),
        (INVOICE_TYPES['extra-ordinary'], 'extra-ordinary')
    ]
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null= True)

    payed = models.BooleanField(default= False)

    invoice_type = models.CharField(
        max_length=1,
        choices=INVOICE_TYPE_CHOICES,
        verbose_name=_('Invoice type'),
    )

    invoice_date = models.DateField(
        verbose_name=_('Invoice date'),
    )

    invoice_number = models.CharField(
        max_length=256,
        verbose_name=_('Invoice No.'),
        blank=True,
    )

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )

    currency = models.ForeignKey(
        'currency_history.Currency',
        related_name='invoices',
        verbose_name=_('Currency'),
        on_delete = models.PROTECT
    )

    amount_net = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        blank=True,
        verbose_name=_('Amount net'),
    )

    vat = models.DecimalField(
        max_digits=14,
        decimal_places=10,
        default=0,
        verbose_name=_('Sales tax'),
        help_text=_("sales tax")
    )

    amount_gross = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        blank=True,
        verbose_name=_('Amount gross'),
    )

    value_net = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Value net'),
    )

    value_gross = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Value gross'),
    )

    payment_date = models.DateField(
        verbose_name=_('Payment date'),
        blank=True,
        null=True,
    )

    pdf = models.FileField(
        upload_to='invoice_files',
        verbose_name=_('PDF'),
        blank=True, null=True,
    )

    objects = InvoiceManager()

    class Meta:
        ordering = ['-invoice_date', '-pk']
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        if self.invoice_number:
            return self.invoice_number
        return '{0} - {1}'.format(self.invoice_date,
                                  self.get_invoice_type_display())

    def notify_client(self):
        NotImplementedError('Method not implemented')

    def save(self, *args, **kwargs):
        self.set_amount_fields()
        self.set_value_fields('invoice_type')
        return super(Invoice, self).save(*args, **kwargs)

    @property
    def balance(self):
        if not self.transactions.all():
            return 0 - self.amount_net

        total = 0
        # Convert amounts
        for currency in Currency.objects.all():
            # Get transactions for each currency
            transactions = self.transactions.filter(currency=currency)
            if not transactions:
                continue

            if currency == self.currency:
                rate = 1
            else:
                rate = Decimal(CurrencyRateHistory.objects.filter(
                    rate__from_currency=currency,
                    rate__to_currency=self.currency,
                )[0].value)
            total += rate * transactions.aggregate(
                models.Sum('amount_net'))['amount_net__sum']
        return total - self.amount_net


@python_2_unicode_compatible
class Payee(models.Model):
    user= models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name=_('Payee'),
        max_length=256,
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _('Payee')
        verbose_name_plural = _('Payees')

    def __str__(self):
        return self.name

    def invoices(self):
        return Invoice.objects.filter(
            pk__in=self.transactions.values_list('invoice__pk')).distinct()


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name


class TransactionManager(models.Manager):
    """Manager for the ``Transaction`` model."""
    def get_totals_by_payee(self, account, start_date=None, end_date=None):
        """
        Returns transaction totals grouped by Payee.

        """
        qs = Transaction.objects.filter(account=account, parent__isnull=True)
        qs = qs.values('payee').annotate(models.Sum('value_gross'))
        qs = qs.order_by('payee__name')
        return qs

    def get_without_invoice(self):
        """
        Returns transactions that don't have an invoice.

        We filter out transactions that have children, because those
        transactions never have invoices - their children are the ones that
        would each have one invoice.

        """
        qs = Transaction.objects.filter(
            children__isnull=True, invoice__isnull=True)
        return qs


@python_2_unicode_compatible
class Transaction(AmountMixin, models.Model):
    TRANSACTION_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
        'pending': 'p',
    }

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPES['withdrawal'], 'withdrawal'),
        (TRANSACTION_TYPES['deposit'], 'deposit'),
        (TRANSACTION_TYPES['pending'], 'pending'),
    ]

    account = models.ForeignKey(
        Account,
        related_name='transactions',
        verbose_name=_('Account'),
        on_delete = models.CASCADE
    )

    parent = models.ForeignKey(
        'account_keeping.Transaction',
        related_name='children',
        blank=True, null=True,
        verbose_name=_('Parent'),
       on_delete = models.CASCADE 
    )

    transaction_type = models.CharField(
        max_length=1,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name=_('Transaction type'),
    )

    transaction_date = models.DateField(
        verbose_name=_('Transaction date'),
        auto_now_add=True
    )

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )

    # invoice_number = models.CharField(
    #     verbose_name=_('Invoice No.'),
    #     max_length=256,
    #     blank=True,
    # )

    invoice = models.ForeignKey(
        Invoice,
        blank=True, null=True,
        related_name='transactions',
        verbose_name=_('Invoice'),
        on_delete = models.PROTECT
    )

    payee = models.ForeignKey(
        User,
        related_name='transactions',
        verbose_name=_('Payee'),
        on_delete = models.PROTECT,
        null= True,
        blank= True
    )

    category = models.ForeignKey(
        Category,
        related_name='transactions',
        verbose_name=_('Category'),
        on_delete = models.PROTECT
    )

    # currency = models.ForeignKey(
    #     'currency_history.Currency',
    #     related_name='transactions',
    #     verbose_name=_('Currency'),
    #     on_delete = models.PROTECT
    # )

    amount_net = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        blank=True,
        verbose_name=_('Amount net'),
    )

    vat = models.DecimalField(
        max_digits=14,
        decimal_places=10,
        default=0,
        verbose_name=_('VAT'),
    )

    amount_gross = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        blank=True,
        verbose_name=_('Amount gross'),
    )

    value_net = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Value net'),
    )

    value_gross = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        default=0,
        verbose_name=_('Value gross'),
    )

    objects = TransactionManager()

    class Meta:
        ordering = ['-transaction_date', '-pk']
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')

    def __str__(self):
        if self.invoice_number:
            return self.invoice_number
        if self.invoice and self.invoice.invoice_number:
            return self.invoice.invoice_number
        return '{0} - {1}'.format(self.payee, self.category)

    def get_description(self):
        if self.description:
            return self.description
        if self.invoice and self.invoice.description:
            return self.invoice.description
        description = ''
        for child in self.children.all():
            if child.description:
                description += u'{0},\n'.format(child.description)
            elif child.invoice and child.invoice.description:
                description += u'{0},\n'.format(child.invoice.description)
        return description or u'n/a'

    def get_invoices(self):
        if self.children.all():
            return [child.invoice for child in self.children.all()]
        return [self.invoice, ]

    def save(self, *args, **kwargs):
        self.set_amount_fields()
        self.set_value_fields('transaction_type')
        return super(Transaction, self).save(*args, **kwargs)

