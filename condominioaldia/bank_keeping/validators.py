import decimal
from  django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_digits(value):
	if value.isdigit() != True:
		raise ValidationError(_('%(value)s is not a number'),params={'value': value},) 


def positive_decimal(value):
	if value< decimal.Decimal(0):
		raise ValidationError(_('Only positive numbers'))
