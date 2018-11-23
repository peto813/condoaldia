import numbers
from django.test import TestCase
from condo_manager.models import Condo, User, Inmueble
from numbers import Number
# Create your tests here.
class CondoTestCase(TestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="peto813@gmail.com", first_name= "residencias kiara")
        condo=Condo.objects.create(user=user, approved=True, terms_accepted= True, active= True)
        Inmueble.objects.create(condo= condo, share= 23, initial_balance = 0, balance = 0, name= '1-a')

    def test_condo_can_get_share_sum(self):
        """Condo can get sum of its properties correctly"""
        user = User.objects.get(email="peto813@gmail.com")
        condo = Condo.objects.get(user=user)
        total = condo.get_share_sum()
        assert 0 <= total <= 100