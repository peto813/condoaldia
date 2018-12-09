import json
from condo_manager.models import User, Condo,Resident, Inmueble #, User, Resident, Rentee
from django.urls import path, re_path
from django.conf.urls import url, include
from django.urls import reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from currency_history.models import Currency
from account_keeping.models import Account, Category, Transaction, Invoice


class ApiEndPointsTestCase(APITestCase, URLPatternsTestCase):
    '''Testing api endpoints'''
    def setUp(self):
        condo_user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", username="condo_user")
        condo=Condo.objects.create( user=condo_user, approved=True, terms_accepted= True, active= True, name='Residencias Isla Paraiso')
        resident_user= User.objects.create(username='resident_user', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0,  name= '1-a', resident = resident)
        condo.inmuebles.add(inmueble)
        currency = Currency.objects.create(iso_code ='PEN', title='Sol Peruano' , abbreviation= 'PEN')
        acc_data= {
            'account_number':'12346579811',
            'name':'test account 2',
            'currency' :currency,
            'user':condo_user
        }
        account2 = Account.objects.create(**acc_data )
        transaction_category = Category.objects.create(name='condo_payment')
        transaction = Transaction.objects.create(
            id=333,
            account = account2,
            transaction_type='p',
            description='test transaction',
            category =transaction_category,
            currency= currency
        )
        # condo_user2= User.objects.create(id_number="j333999988", mobile="04140934140", email ="123@gmail.com", username="condo_user2")
        # condo=Condo.objects.create( user=condo_user2, approved=True, terms_accepted= True, active= True, name='Residencias Kiara')


    urlpatterns = [
        path('condos/', include('account_keeping.urls')),
    ]


    #account
    def test_condo_and_resident_can_get_account_info(self):
        '''Accounts can be retrieved by residents and condo'''
        condo_user = User.objects.get(username="condo_user")
        account= condo_user.bank_accounts.all().first()
        url = reverse('account_keeping:account-detail',kwargs={'pk':account.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    #account
    def test_only_condo_can_create_accounts(self):
        '''Accounts can only be created by condos'''
        condo_user = User.objects.get(username="condo_user")
        url = reverse('account_keeping:account-list')
        self.client.force_authenticate(user=condo_user)
        currency= Currency.objects.get(iso_code='PEN')
        acc_data= {
            'account_number':'123465798',
            'name':'test account',
            'currency' :currency.pk,
        }
        response=self.client.post(url, acc_data, format= 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.post(url, acc_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_condo_can_update_accounts(self):
        '''Account can only be updated by condo owner'''
        condo_user = User.objects.get(username="condo_user")
        account= condo_user.bank_accounts.all().first()
        url = reverse('account_keeping:account-detail',kwargs={'pk':account.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.patch(url, {'active': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.patch(url, {'active': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_condo_can_delete_accounts(self):
        '''Account can only be deleted by condo owner'''
        condo_user = User.objects.get(username="condo_user")
        account= condo_user.bank_accounts.all().first()
        url = reverse('account_keeping:account-detail',kwargs={'pk':account.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #transactions
    def test_condo_and_resident_can_create_transactions(self):
        '''Resident and Condo can create transactions'''
        condo_user = User.objects.get(username="condo_user")
        account= condo_user.bank_accounts.all().first()
        currency= Currency.objects.get(iso_code='PEN')
        url = reverse('account_keeping:transaction-list',kwargs={'account_pk':account.pk})
        self.client.force_authenticate(user=condo_user)
        transaction_category= Category.objects.get(name="condo_payment")
        data ={'category':transaction_category.pk,'account':account.pk, 'transaction_type':'d','currency':currency.pk}
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.post(url, data, format= 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_only_condo_update_transactions(self):
        '''Transactions can only be updated by condo'''
        condo_user = User.objects.get(username="condo_user")
        transaction= Transaction.objects.get(id=333)
        account= Account.objects.all().first()
        url = reverse('account_keeping:transaction-detail', kwargs={'account_pk':account.pk, 'pk':transaction.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.patch(url, {'transaction_type':'w'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.patch(url, {'transaction_type':'p'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_only_deposits_can_be_created_by_resident(self):
        '''The only transaction type allowed for creation by resident is deposit'''
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        account= Account.objects.all().first()
        currency= Currency.objects.get(iso_code='PEN')
        transaction_category= Category.objects.get(name="condo_payment")
        url = reverse('account_keeping:transaction-list', kwargs={'account_pk':account.pk})
        data ={'category':transaction_category.pk,'account':account.pk, 'transaction_type':'w','currency':currency.pk}
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data ={'category':transaction_category.pk,'account':account.pk, 'transaction_type':'d','currency':currency.pk}
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # def test_invoice_can_only_be_created_by_condos(self):
    #     '''Invoices can only be created by condos'''

    #     #condo case
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     #resident case
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)