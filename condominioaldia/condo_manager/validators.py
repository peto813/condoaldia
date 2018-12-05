from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_postitive(value):
	if value <0:
		raise ValidationError(
			_('%(value)s is not a positive amount.'),
			params={'value': value},
		)