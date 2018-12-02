import numbers, json, PIL, tempfile
from django.urls import path, re_path
from django.test import TestCase, Client
from condo_manager.models import Resident, Condo, User, Inmueble, Resident
from currency_history.models import Currency
from numbers import Number
from django.urls import reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from django.conf.urls import url, include
from rest_framework.authtoken.models import Token
#from PIL import Image
'''
NOTES

The condo_manager app uses singals where sometimes the instance is passed with an optional
request attribute. This should be addressed for testing purposes
'''

# Create your tests here.
class ApiEndPointsTestCase(APITestCase, URLPatternsTestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara", username="user1")
        condo=Condo.objects.create(user=user, approved=False, terms_accepted= True, active= True, razon_social='Residencias Isla Paraiso')
        resident_user= User.objects.create(username='b', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)

    urlpatterns = [
        #path('api-auth/', include('rest_framework.urls')),
        #path('accounts/', include('allauth.urls')),
        path('condos/', include('condo_manager.urls')),
        #path('condos/', include('account_keeping.urls')),
        path('condos/registration/', include('rest_auth.registration.urls')),
        #path('condos/', include('rest_auth.urls')),
    ]
    def test_post_condo_registration(self):
        with open('/home/einstein/condominioaldia/condominioaldia/static/project_static/img/logos/logo.png', 'rb') as img:
            data = {
                'email': 'peto813ss@gmaisssl.com',
                'password1': 'ou63ut14',
                'password2': 'ou63ut14',
                'terms':True,
                'id_number':'j401878s746',
                'id_proof':img
            }
            response=self.client.post('/condos/registration/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_condo_details(self):
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        url = reverse('condo_manager:condo-detail', kwargs={'condo_id':condo.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_details(self):
        user = User.objects.get(email="12@gmail.com")
        url = reverse('condo_manager:user-detail', kwargs={'pk':user.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_resident_details(self):
        resident_user = User.objects.get(email="averga@hotmail.com")
        resident= Resident.objects.get(user= resident_user)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident.pk})
        self.client.force_authenticate(user=resident_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CondoTestCase(APITestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara", username="user1")
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

# class ResidentTestCase(TestCase):
	
# 	def setUp(self):
# 		user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara")
# 		resident= Resident.objects.create(user= user)
		
