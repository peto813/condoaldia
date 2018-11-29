import numbers
from django.test import TestCase
from condo_manager.models import Resident, Condo, User, Inmueble, Resident
from currency_history.models import Currency
from numbers import Number

'''
NOTES

The condo_manager app uses singals where sometimes the instance is passed with an optional
request attribute. This should be addressed for testing purposes
'''


# Create your tests here.
class CondoTestCase(TestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara")
        condo=Condo.objects.create(user=user, approved=False, terms_accepted= True, active= True)
        inmueble= Inmueble.objects.create(condo= condo, share= 23, initial_balance = 0, balance = 0, name= '1-a')
        currency = Currency.objects.create(iso_code='USD',title='bolivar soberano', abbreviation= 'Bs')
        #account = Currency.objects.create(iso_code='USD',title='bolivar soberano', abbreviation= 'Bs')
    def test_condo_can_get_share_sum(self):
        """Condo can get sum of its properties correctly"""
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        total = condo.get_share_sum()
        assert 0 <= total <= 100

    def test_condo_approval(self):
        """Condo can get sum of its properties correctly"""
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        assert (condo.approval_date ==None)
        condo.approve()
        assert  (condo.approval_date !=None)

    def test_create_bank_account(self):
        """Condo can get sum of its properties correctly"""
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        currency = Currency.objects.get(iso_code='USD')
        data ={
            'name':'usd account',
            'account_number': '01340262142623025724',
            'currency': currency
        }
        condo.create_bank_account(data)
        # assert (condo.approval_date ==None)
        # condo.approve()
        # assert  (condo.approval_date !=None)

class InmuebleTestCase(TestCase):
    def setUp(self):
        condo_user= User.objects.create(username='a', id_number="J8309921", mobile="04140934140", email ="colio@gmail.com", first_name= "residencias kiara")
        condo=Condo.objects.create(user=condo_user, approved=True, terms_accepted= True, active= True)
        inmueble= Inmueble.objects.create(condo= condo, share= 23, initial_balance = 0, balance = 0, name= '1-a')
        resident_user= User.objects.create(username='b', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
    
    def test_inmueble_owner_change_signal(self):
        """Condo can get sum of its properties correctly"""

        inmueble= Inmueble.objects.get(id=1)
        resident_user= User.objects.get(username='b')
        resident = Resident.objects.get(user=resident_user)
        inmueble.resident= resident
        inmueble.save()

class ResidentTestCase(TestCase):
	
	def setUp(self):
		user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara")
		resident= Resident.objects.create(user= user)
		
