import json, decimal, arrow, time
from django.utils import timezone
from condo_manager.models import User, Condo,Resident, Inmueble #, User, Resident, Rentee
from django.urls import path, re_path
from django.conf.urls import url, include
from django.urls import reverse
from rest_framework.test import APITestCase, APITransactionTestCase, URLPatternsTestCase
from rest_framework import status
from currency_history.models import Currency
from account_keeping.models import Account, Category, Transaction, Invoice, Order
from rest_framework.routers import DefaultRouter
from account_keeping.views import InvoiceViewSet

SLOW_TEST_THRESHOLD = 0.1


class ApiEndPointsTestCase(APITransactionTestCase, URLPatternsTestCase):
    '''Testing api endpoints'''
    router= DefaultRouter()
    router.register(r'invoices', InvoiceViewSet, basename="invoice")

    urlpatterns = [
        path('condos/', include('condo_manager.urls', namespace='condo_manager')),
        path('condos/accounts/', include('account_keeping.urls', namespace='account_keeping')),
        path('condos/',  include(router.urls)),
    ]

    def setUp(self):
        self._started_at = time.time()
        condo_user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", username="condo_user")
        condo=Condo.objects.create( user=condo_user, approved=True, terms_accepted= True, active= True, name='Residencias Isla Paraiso')
        condo_user2= User.objects.create(id_number="J8309921", mobile="04140934141", email ="121@gmail.com", username="condo_user2")
        condo2=Condo.objects.create( user=condo_user2, approved=True, terms_accepted= True, active= True, name='Residencias Pueblo viejo')
        resident_user= User.objects.create(username='resident_user', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        resident_user2= User.objects.create(username='resident_user2', id_number="v6750436", mobile="041467934146", email ="resident2@hotmail.com", first_name= "kristo", last_name= "ranka")
        resident2= Resident.objects.create(user= resident_user2)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0,  name= '1-a', resident = resident)
        inmueble2= Inmueble.objects.create(condo= condo2, share= 0.35, initial_balance = 0,  name= 'agora 9-b', resident = resident2)
        currency = Currency.objects.create(iso_code ='PEN', title='Sol Peruano' , abbreviation= 'PEN')
        acc_data= {
            'account_number':'12346579811',
            'name':'test account 2',
            'currency' :currency,
            'user':condo_user
        }
        account = Account.objects.create(**acc_data )
        transaction_category = Category.objects.create(name='condo_payment')
        transaction = Transaction.objects.create(
            id=333,
            account = account,
            transaction_type='p',
            description='test transaction',
            category =transaction_category,
            transaction_date = timezone.now()
        )

        order= Order.objects.create(**{
            "condo": condo,
            "order_type": "d",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"invoice_number": "123456789",
            "amount_gross": 20,
            "currency": currency
        })

        invoice_data={
            "condo": condo,
            "invoice_type": "d",
            'invoice_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            "invoice_number": "123456789",
            "order":order
            #"amount_gross": 20,
            #"currency": currency
        }
        invoice = Invoice.objects.create(**invoice_data)

    def tearDown(self):
        elapsed = time.time() - self._started_at
        if elapsed > SLOW_TEST_THRESHOLD:
            print('{} ({}s)'.format(self.id(), round(elapsed, 2)))
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
        response=self.client.post(url, acc_data)
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
        data ={
            'transaction_date':arrow.now().format(fmt='YYYY-MM-DD', locale='en_us'),
            'category':transaction_category.pk,
            'account':account.pk,
            'transaction_type':'d',
            'currency':currency.pk
        }
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


    def test_transactions_prohibited_for_update_for_closed_month(self):
        '''Transactions can not be created for a closed month'''
        condo_user = User.objects.get(username="condo_user")
        transaction= Transaction.objects.get(id=333)
        invoice= Invoice.objects.all().first()
        invoice.invoice_type='m'
        invoice.save()
        url = reverse('account_keeping:transaction-detail', kwargs={'account_pk':transaction.account.pk, 'pk':transaction.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.patch(url, {'transaction_type':'w'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_transactions_prohibited_for_insert_for_closed_month(self):
    #     '''Transactions can not be modified for a closed month'''
    #     condo_user = User.objects.get(username="condo_user")
    #     transaction= Transaction.objects.get(id=333)
    #     invoice= Invoice.objects.all().first()
    #     invoice.invoice_type='m'
    #     invoice.save()
    #     account= condo_user.bank_accounts.all().first()
    #     currency= Currency.objects.get(iso_code='PEN')

    #     transaction_category= Category.objects.get(name="condo_payment")
    #     url = reverse('account_keeping:transaction-list', kwargs={'account_pk':transaction.account.pk})
    #     self.client.force_authenticate(user=condo_user)
    #     data ={
    #         'transaction_date':arrow.now().format(fmt='YYYY-MM-DD', locale='en_us'),
    #         'category':transaction_category.pk,
    #         'account':account.pk,
    #         'transaction_type':'d',
    #         'currency':currency.pk
    #     }
    #     response=self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_residents_can_only_create_transaction_type_deposit(self):
        '''The only transaction type allowed for creation by resident is deposit'''
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        account= Account.objects.all().first()
        currency= Currency.objects.get(iso_code='PEN')
        transaction_category= Category.objects.get(name="condo_payment")
        url = reverse('account_keeping:transaction-list', kwargs={'account_pk':account.pk})
        data ={
            'category':transaction_category.pk,
            'account':account.pk,
            'transaction_type':'w',
            'currency':currency.pk,
            'transaction_date':  arrow.now().format(fmt='YYYY-MM-DD', locale='en_us'),
            'mark_invoice' : False
        }
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data2 ={
            'category':transaction_category.pk,
            'account':account.pk,
            'transaction_type':'d',
            'currency':currency.pk,
            'transaction_date':  arrow.now().format(fmt='YYYY-MM-DD', locale='en_us'),
            'mark_invoice' : False
        }
        response=self.client.post(url, data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)




    def test_condo_can_only_view_its_own_transactions(self):
        '''Condos can only view its own transactions'''
        condo_user = User.objects.get(username = 'condo_user')
        condo_user2 = User.objects.get(username = 'condo_user2')
        self.client.force_authenticate(user=condo_user2)
        transaction= Transaction.objects.get(id=333)
        account= Account.objects.all().first() 
        url = reverse('account_keeping:transaction-detail', kwargs={'account_pk':account.pk, 'pk':transaction.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=condo_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_can_only_view_its_condo_transactions(self):
        '''Resident can only view its condos transactions'''
        condo_user = User.objects.get(username = 'condo_user')
        condo_user2 = User.objects.get(username = 'condo_user2')
        resident_user = User.objects.get(username="resident_user")
        resident_user2 = User.objects.get(username="resident_user2")
        transaction= Transaction.objects.get(id=333)
        account= Account.objects.all().first()
        self.client.force_authenticate(user=resident_user)
        url = reverse('account_keeping:transaction-detail', kwargs={'account_pk':account.pk, 'pk':transaction.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=resident_user2)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_condo_can_create_expense_for_period_only(self):
        '''Condo can not post transaction type withdrawal outside correct period '''
        condo_user= User.objects.get(username='condo_user')
        self.client.force_authenticate(user=condo_user)
        account= condo_user.bank_accounts.all().first()
        period_date = condo_user.condo.get_current_billing_period()['from']
        url = reverse('account_keeping:transaction-list',kwargs={'account_pk':account.pk})
        transaction_data= {
            'transaction_type':'w',
            'description':'Compra de cabañas y cabíllas',
            'amount_gross':4463.9,
            'transaction_date': arrow.get(period_date).format(fmt='YYYY-MM-DD', locale='en_us')
        }
        response= self.client.post(url, transaction_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_data2= {
            'transaction_type':'w',
            'description':'second purchase',
            'amount_gross':100.9,
            'transaction_date': arrow.get(period_date).format(fmt='YYYY-MM-DD', locale='en_us')
        }
        response= self.client.post(url, transaction_data2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        transaction_data3= {
            'transaction_type':'w',
            'description':'second purchase',
            'amount_gross':10220.9,
            'transaction_date': '2020-01-01'
        }
        response= self.client.post(url, transaction_data3)
        #NO TRANSACTIONS BEYOND TODAY(THE FUTURE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    #invoices
    def test_only_one_monthly_invoice_per_month(self):
        '''Invoice only allows one monthly invoice per calendar month'''
        condo_user = User.objects.get(username="condo_user")
        self.client.force_authenticate(user=condo_user)
        url = reverse('invoice-list')
        currency= Currency.objects.get(iso_code='PEN')
        now = utc = arrow.utcnow().replace(months=-3).datetime.date()
        order= Order.objects.create(**{
            "condo": condo_user.condo,
            "order_type": "d",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"invoice_number": "123456789",
            "amount_gross": 20,
            "currency": currency,
            
        })
        data= {
            'invoice_type': 'm',
            'invoice_date':now,
            #'currency':currency.pk,
            'amount_gross': 455.89,
            'order':order.pk

        }  
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data['invoice_date'] = arrow.get(now).replace(months=+1).datetime.date()
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data['invoice_date'] = arrow.get(now).replace(months=+2).datetime.date()
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data['amount_gross'] = 333.33
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_post_for_month_with_monthly_invoice(self):
        '''once a month has a monthly invoice, no invoices can be posted there'''
        condo_user = User.objects.get(username="condo_user")
        self.client.force_authenticate(user=condo_user)
        url = reverse('invoice-list')
        currency= Currency.objects.get(iso_code='PEN')
        now = utc = arrow.utcnow().replace(months=-3).datetime.date()
        order= Order.objects.create(**{
            "condo": condo_user.condo,
            "order_type": "m",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"invoice_number": "123456789",
            "amount_gross": 20,
            "currency": currency
        })
        data= {
            'invoice_type': 'm',
            'invoice_date':now,
            'currency':currency.pk,
            'amount_gross': 455.89,
            'order':order.pk

        }  
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data['invoice_date'] = arrow.get(now).replace(months=+2).datetime.date()
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        data['invoice_type'] = 'd'
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invoice_marked_as_payed(self):
        '''Invoice can be marked as payed'''
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        account= Account.objects.all().first()
        currency= Currency.objects.get(iso_code='PEN')
        transaction_category= Category.objects.get(name="condo_payment")
        url = reverse('account_keeping:transaction-list', kwargs={'account_pk':account.pk})
        invoice = Invoice.objects.get(invoice_number=123456789)

        data ={
            'category':transaction_category.pk,
            'account':account.pk,
            'transaction_type':'d',
            'currency':currency.pk,
            'transaction_date':  arrow.now().format(fmt='YYYY-MM-DD', locale='en_us'),
            'mark_invoice' : True,
            'invoice' : invoice.pk
        }
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invoice_can_only_be_created_by_condos(self):
        '''Invoices can only be created by condos'''
        condo_user = User.objects.get(username="condo_user")
        self.client.force_authenticate(user=condo_user)
        url = reverse('invoice-list')
        currency= Currency.objects.get(iso_code='PEN')
        order= Order.objects.create(**{
            "condo": condo_user.condo,
            "order_type": "d",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"invoice_number": "123456789",
            "amount_gross": 20,
            "currency": currency
        })
        data= {
            'invoice_type': 'd',
            'invoice_date':timezone.now().date(),
            'currency':currency.pk,
            'amount_gross': 455.89,
            'order':order.pk

        }  
        #condo case
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #resident case
        resident_user = User.objects.get(username="resident_user")
        self.client.force_authenticate(user=resident_user)
        response=self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_invoice_monthly_boundaries(self):
        '''Invoice monthly boundaries tested '''
        condo_user = User.objects.get(username="condo_user")
        self.client.force_authenticate(user=condo_user)
        url = reverse('invoice-list')
        currency= Currency.objects.get(iso_code='PEN')
        first_date = arrow.utcnow().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
        first_invoice =Invoice.objects.all().first()
        order= Order.objects.create(**{
            "condo": condo_user.condo,
            "order_type": "d",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"invoice_number": "123456789",
            "amount_gross": 20,
            "currency": currency,
            
        })
        data= {
            'invoice_type': 'd',
            'invoice_date':arrow.get(first_invoice.invoice_date).format(fmt='YYYY-MM-DD', locale='en_us'),
            #'currency':currency.pk,
            "order":order.pk

        }  
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #testing end of first month
        end_month = arrow.get(first_invoice.invoice_date).ceil('month').format(fmt='YYYY-MM-DD', locale='en_us')
        data['invoice_date'] = end_month

        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        #add monthly invoice
        data['invoice_type'] = 'm'
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #attempting another invoice for this given month
        data['invoice_type'] = 'w'
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        #attempting first moment of following month
        first_moment_following_month = arrow.get(first_invoice.invoice_date).replace(months=+1).floor('month').format(fmt='YYYY-MM-DD', locale='en_us')
        data['invoice_date'] = first_moment_following_month
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #attempting first moment of following month fail
        last_moment_last_month = arrow.get(first_invoice.invoice_date).replace(months=+1).floor('month').shift(seconds=-1).format(fmt='YYYY-MM-DD', locale='en_us')
        data['invoice_date'] = last_moment_last_month
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
