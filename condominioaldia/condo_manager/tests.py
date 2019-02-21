import numbers, json, PIL, tempfile, os, decimal, arrow, time
from django.utils import timezone
from django.urls import path, re_path
from django.test import TestCase, Client
from condo_manager.models import Resident, Condo, User, Inmueble, Resident, Rentee
from currency_history.models import Currency
from numbers import Number
from django.urls import reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from django.conf.urls import url, include
from rest_framework.authtoken.models import Token
from rolepermissions.checkers import has_permission, has_role
from django.conf import settings
from django.core import mail
from rest_framework.routers import DefaultRouter
from condo_manager import views



SLOW_TEST_THRESHOLD = 0.3

class ApiEndPointsTestCase(APITestCase, URLPatternsTestCase):
    '''Testing api endpoints'''
    def setUp(self):
        self._started_at = time.time()
        condo_user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara", username="user1")
        condo=Condo.objects.create( user=condo_user, approved=True, terms_accepted= True, active= True, name='Residencias Isla Paraiso')
        resident_user= User.objects.create(username='b', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0,  name= '1-a')
        #condo.inmuebles.add(inmueble)
    router= DefaultRouter()
    router.register(r'user', views.UserViewSet)
    urlpatterns = [
        #path('api-auth/', include('rest_framework.urls')),
        #path('accounts/', include('allauth.urls')),
        path('condos/', include('condo_manager.urls')),
        #path('condos/', include('account_keeping.urls')),
        path('condos/registration/', include('rest_auth.registration.urls')),
        #/users/password/reset/
        path('users/',  include(router.urls))
    ]

    def tearDown(self):
        elapsed = time.time() - self._started_at
        if elapsed > SLOW_TEST_THRESHOLD:
            print('{} ({}s)'.format(self.id(), round(elapsed, 2)))
    #user
    def test_get_user_details(self):
        user = User.objects.get(email="12@gmail.com")
        url = reverse('condo_manager:user-detail', kwargs={'pk':user.pk})
        self.client.force_authenticate(user=user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_request_pwd_reset(self):
        '''User can successfully request a password reset via api endpoint '''
        pass

    #condo
    def test_post_condo_registration(self):
        file_path= os.path.join(settings.BASE_DIR, "static", "project_static", "img", 'logos')
        with open(file_path+ '/logo.png', 'rb') as img:
            data = {
                'email': 'peto813ss@gmaisssl.com',
                'password1': 'ou63ut14',
                'password2': 'ou63ut14',
                'terms':True,
                'id_number':'j401878s746',
                'id_proof':img,
                'name': 'condo 1'
            }
            response=self.client.post('/condos/registration/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

    def test_get_condo_details(self):
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo.pk})
        self.client.force_authenticate(user=user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_modify_condo(self):
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo.pk})
        self.client.force_authenticate(user=user)
        response=self.client.patch(url, {'approved':True, 'name':'i rule'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #properties(inmuebles)

    def test_list_condo_properties(self):
        '''Condo can list its properties'''
        user = User.objects.get(email="12@gmail.com")
        url = reverse('condo_manager:inmueble-list')
        self.client.force_authenticate(user=user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_condo_property_detail(self):
        '''User retrieves property information'''
        condo_user = User.objects.get(email="12@gmail.com")
        inmueble = Inmueble.objects.get(name= '1-a')
        url = reverse('condo_manager:inmueble-detail', kwargs={'pk':inmueble.pk})
        self.client.force_authenticate(user=condo_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_post_property(self):
        '''Condo can create properties'''
        property1 = {
            'share': decimal.Decimal(0.09),
            'initial_balance': decimal.Decimal(2),
            'name': 'PH1',
        }
        condo_user= User.objects.get( email ="12@gmail.com")
        url = reverse('condo_manager:inmueble-list')
        self.client.force_authenticate(user=condo_user)
        response=self.client.post(url, property1)
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)

    def test_post_property_over_100(self):
        '''Condo validation kicks in given a sum over 1 of condo shares'''
        property2 = {
            'share': decimal.Decimal(200),
            'initial_balance': decimal.Decimal(2),
            'name': 'PH2',
        }
        condo_user= User.objects.get( email ="12@gmail.com")
        url = reverse('condo_manager:inmueble-list')
        self.client.force_authenticate(user=condo_user)
        response=self.client.post(url, property2)
        self.assertEqual(response.status_code,  status.HTTP_400_BAD_REQUEST)


    def test_property_share_negative(self):
        '''Validators raise error when condo posts negative share values'''
        property2 = {
            'share': decimal.Decimal(-1),
            'initial_balance': decimal.Decimal(2),
            'name': 'PH2',
        }
        condo_user= User.objects.get( email ="12@gmail.com")
        url = reverse('condo_manager:inmueble-list')
        self.client.force_authenticate(user=condo_user)
        response=self.client.post(url, property2)
        self.assertEqual(response.status_code,  status.HTTP_400_BAD_REQUEST)


    def test_get_resident_details(self):
        '''User can get details for a particular resident(NEEDS TWEAKING)'''
        resident_user = User.objects.get(email="averga@hotmail.com")
        resident= Resident.objects.get(user= resident_user)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident.pk})
        self.client.force_authenticate(user=resident_user)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserTestCase(APITestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara", username="user", last_name='C.A.')
        user1= User.objects.create(id_number="J83099201", mobile="04140934140", email ="123@gmail.com", username="user1")
        condo_user= User.objects.create(id_number="J3688076", mobile="04140934140", email ="1234@gmail.com", username="user2")
        condo=Condo.objects.create( user=condo_user, approved=True, terms_accepted= True, active= True, name='Residencias Isla Paraiso')

    def test_user_get_full_name_with_first_or_last_name(self):
        """User can get its full name when provided first and last name"""
        user = User.objects.get(email="12@gmail.com")
        full_name= user.full_name
        assert full_name != None

    def test_user_get_full_name_without_first_or_last_name(self):
        """User can get its full name when only provided with email"""
        user = User.objects.get(email="123@gmail.com")
        full_name= user.full_name
        assert full_name != None

    def test_user_get_full_name_with_company_name(self):
        """User can get its full name when  its condo"""
        user = User.objects.get(email="1234@gmail.com")
        full_name= user.full_name
        assert full_name != None


class CondoTestCase(APITestCase):
    def setUp(self):
        user= User.objects.create(id_number="J8309920", mobile="04140934140", email ="12@gmail.com", first_name= "residencias kiara", username="user1")
        condo=Condo.objects.create(user=user, approved=False, terms_accepted= True, active= True)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0, name= '1-a')
        currency = Currency.objects.create(iso_code='USD',title='bolivar soberano', abbreviation= 'Bs')

    # def test_condo_can_bill_properties(self):
    #     """Condo can create monthly bill for every property"""
    #     user = User.objects.get(email="12@gmail.com")
    #     condo = Condo.objects.get(user=user)
    #     condo.create_monthly_bill()
    #     # currency = Currency.objects.get(iso_code='USD')
    #     # data ={
    #     #     'name':'usd account',
    #     #     'account_number': '01340262142623025724',
    #     #     'currency': currency
    #     # }
    #     # condo.create_bank_account(data)


    def test_condo_can_get_share_sum(self):
        """Condo can get sum of all of its property shares"""
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        total = condo.get_share_sum()
        assert 0 <= total <= 100

    def test_condo_approval(self):
        """Condo can be properly approved by admins"""
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        assert (condo.approval_date ==None)
        condo.approve()
        assert  (condo.approval_date !=None)
        self.assertEqual(len(mail.outbox), 1)

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

    def test_condo_can_get_current_period(self):
        """Condo can correctly get its current billing period"""
        keys= ['from', 'to']
        user = User.objects.get(email="12@gmail.com")
        condo = Condo.objects.get(user=user)
        current_period = condo.get_current_billing_period()
        #no invoices yet to initial period is month joined
        expected_response= {
            'from': arrow.get(user.date_joined).floor('month').datetime,
            'to':arrow.get(user.date_joined).ceil('month').datetime
        }
        assert expected_response == current_period
        assert 'from' and 'to' in current_period
        currency = Currency.objects.get(iso_code='USD')
        
        order_data= {
            "condo": condo,
            "order_type": "d",
            'order_date':  arrow.now().replace(months=-10).format(fmt='YYYY-MM-DD', locale='en_us'),
            #"order_number": "123456789",
            "description": "you are here, with the in-voice, get it?",
            "amount_gross": 20,
            "currency": currency,
            "customer_id":1
        }
        order= condo.orders.create(**order_data)
        #add a monthly invoice and check new expected response
        invoice = condo.user.invoices.create(
            invoice_date = timezone.now().date(),
            order = order,
            invoice_type= 'm',
            user = condo.user
        )
        current_period = condo.get_current_billing_period()
        latest_monthly_invoice = condo.user.invoices.all().latest('invoice_date')
        next_monthly_invoice_date=arrow.get(latest_monthly_invoice.invoice_date).ceil('month').replace(seconds=+1)
        expected_response2= {
            'from' :next_monthly_invoice_date.floor('month').datetime,
            'to':next_monthly_invoice_date.ceil('month').datetime
        }
        assert expected_response2 == current_period





class InmuebleTestCase(TestCase):
    def setUp(self):
        condo_user= User.objects.create(username='a', id_number="J8309921", mobile="04140934140", email ="colio@gmail.com", first_name= "residencias kiara")
        condo=Condo.objects.create(user=condo_user, approved=True, terms_accepted= True, active= True)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0, name= '1-a')
        resident_user= User.objects.create(username='b', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        rentee_user= User.objects.create(username='c', id_number="J8309922", mobile="04140934140", email ="colio2@gmail.com", first_name= "el inquilino", last_name="mayor")
        now = timezone.now()
        rentee=Rentee.objects.create(user=rentee_user, since = now)

    def test_can_get_balance(self):
        ''' Property can determine its balance'''
        pass
        # inmueble = Inmueble.objects.get(id=1)
        # inmueble.board_position= 'President'
        # assert inmueble.is_board_member == True

    
    def test_inmueble_owner_change_signal(self):
        '''Property object can change owner and fires the signal'''
        inmueble= Inmueble.objects.get(name='1-a')
        resident_user= User.objects.get(username='b')
        resident = Resident.objects.get(user=resident_user)
        inmueble.resident= resident
        inmueble.save()

    def test_is_not_rented(self):
        ''' Property can determine if it is NOT rented '''
        inmueble= Inmueble.objects.get(name='1-a')
        assert inmueble.is_rented == False

    def test_is_not_board_member(self):
        ''' Property can determine if it is NOT a board member '''
        inmueble= Inmueble.objects.get(name='1-a')
        assert inmueble.is_board_member == False


    def test_is_rented(self):
        ''' Property can determine if it is rented '''
        inmueble= Inmueble.objects.get(name='1-a')
        user = User.objects.get(email='colio2@gmail.com')
        inmueble.rentee= user.rentee
        assert inmueble.is_rented == True

    def test_is_board_member(self):
        ''' Property can determine if it is a board member '''
        inmueble= Inmueble.objects.get(name='1-a')
        inmueble.board_position= 'President'
        assert inmueble.is_board_member == True



class ResidentTestCase(TestCase):

    def setUp(self):
        condo_user= User.objects.create(username='a', id_number="J8309921", mobile="04140934140", email ="colio@gmail.com", first_name= "residencias kiara")
        condo=Condo.objects.create(user=condo_user, approved=True, terms_accepted= True, active= True)
        inmueble= Inmueble.objects.create(condo= condo, share= 0.5, initial_balance = 0, name= '1-a')
        resident_user= User.objects.create(username='b', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        

    def test_resident_send_welcome_email(self):
        '''Resident model sends welcome email'''
        inmueble= Inmueble.objects.get(name='1-a')
        resident_user= User.objects.get(username='b')
        resident = Resident.objects.get(user=resident_user)
        resident.send_welcome_email(inmueble)
        self.assertEqual(len(mail.outbox), 1)


class PermissionTestCase(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        #path('api-auth/', include('rest_framework.urls')),
        #path('accounts/', include('allauth.urls')),
        path('condos/', include('condo_manager.urls')),
        #path('condos/', include('account_keeping.urls')),
        path('condos/registration/', include('rest_auth.registration.urls')),
        #path('condos/', include('rest_auth.urls')),
    ]
    def setUp(self):
        condo_user1= User.objects.create(username='condo_user1', id_number="J8309921", mobile="04140934140", email ="colio@gmail.com", first_name= "residencias kiara")
        condo1=Condo.objects.create(user=condo_user1, approved=True, terms_accepted= True, active= True)
        condo_user2= User.objects.create(username='condo_user2', id_number="J830992a", mobile="04140934140", email ="colio@gmasil.com", first_name= "residencias kiasra 2")
        condo2 = Condo.objects.create(user=condo_user2, approved=True, terms_accepted= True, active= True)    
        resident_user= User.objects.create(username='c', id_number="v6750435", mobile="041467934140", email ="averga@hotmail.com", first_name= "einstein", last_name= "millan")
        resident= Resident.objects.create(user= resident_user)
        resident_user2= User.objects.create(username='d', id_number="v67504351", mobile="041467934140", email ="avergssa@hotmail.com", first_name= "a", last_name= "b")
        resident2= Resident.objects.create(user= resident_user2)      
        #condo1.inmuebles.add(inmueble)
        inmueble= Inmueble.objects.create(condo= condo1, share= 0.5, initial_balance = 0, name= '1-a', resident= resident)
        inmueble2= Inmueble.objects.create(condo= condo1, share= 0.1, initial_balance = 0, name= '1-b')
        condo1.inmuebles.add(inmueble)
        condo1.inmuebles.add(inmueble2)
    #CONDO VIEW PERMISSIONS
    def test_condo_can_not_access_other_condos(self):
        '''Condo cant access other condos'''
        condo_user1= User.objects.get(username='condo_user1')
        condo1 = Condo.objects.get(user = condo_user1)
        condo_user2= User.objects.get(username='condo_user2')
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo1.pk})
        self.client.force_authenticate(user=condo_user2)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_condo_can_see_itself(self):
        '''Condo can access itself'''
        condo_user1= User.objects.get(username='condo_user1')
        condo1 = Condo.objects.get(user = condo_user1)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo1.pk})
        self.client.force_authenticate(user=condo_user1)
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_condo_can_not_see_other_condo_residents(self):
        '''Condo cant access other condos residents'''
        condo_user2= User.objects.get(username='condo_user2')
        self.client.force_authenticate(user=condo_user2)
        resident_user= User.objects.get(username='c')
        resident= Resident.objects.get(user= resident_user)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_condo_can_see_its_residents(self):
        '''Condo can access its residents'''
        condo_user1= User.objects.get(username='condo_user1')
        self.client.force_authenticate(user=condo_user1)
        resident_user= User.objects.get(username='c')
        resident= Resident.objects.get(user= resident_user)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #RESIDENT VIEW PERMISSIONS
    def test_resident_cant_view_other_residents(self):
        '''Resident can not view other residents'''
        resident_user= User.objects.get(username='c')
        resident_user2= User.objects.get(username='d')
        self.client.force_authenticate(user=resident_user)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident_user2.resident.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_can_not_create_residents(self):
        '''Resident can not create residents'''
        resident_user= User.objects.get(username='c')
        self.client.force_authenticate(user=resident_user)
        url = reverse('condo_manager:resident-list')
        post_data={}
        response=self.client.post(url, post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_resident_can_not_view_unrelated_condos(self):
        '''Resident can not access other condos'''
        condo_user2= User.objects.get(username='condo_user2')
        condo2 = Condo.objects.get(user = condo_user2)
        resident_user= User.objects.get(username='c')
        self.client.force_authenticate(user=resident_user)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo2.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_can_view_its_condo(self):
        '''Resident can see its condo'''
        condo_user1= User.objects.get(username='condo_user1')
        condo1 = Condo.objects.get(user = condo_user1)
        resident_user= User.objects.get(username='c')
        self.client.force_authenticate(user=resident_user)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo1.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_resident_can_not_edit_its_condo(self):
        '''Resident can not edit its condo'''
        condo_user1= User.objects.get(username='condo_user1')
        condo1 = Condo.objects.get(user = condo_user1)
        resident_user= User.objects.get(username='c')
        self.client.force_authenticate(user=resident_user)
        url = reverse('condo_manager:condo-detail', kwargs={'pk':condo1.pk})
        response=self.client.patch(url, { 'name':'diff name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_can_view_self(self):
        '''Resident can not edit its condo'''
        resident_user2= User.objects.get(username='d')
        self.client.force_authenticate(user=resident_user2)
        url = reverse('condo_manager:resident-detail', kwargs={'pk':resident_user2.resident.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    #USER VIEW PERMISSIONS
    def test_user_can_not_edit_other_users(self):
        '''User can not edit other users'''
        condo_user1= User.objects.get(username='condo_user1')
        condo_user2= User.objects.get(username='condo_user2')
        url = reverse('condo_manager:user-detail', kwargs={'pk':condo_user2.pk})
        self.client.force_authenticate(user=condo_user1)
        response=self.client.patch(url, { 'first_name':'diff name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_edit_self(self):
        '''User can edit self'''
        condo_user1= User.objects.get(username='condo_user1')
        url = reverse('condo_manager:user-detail', kwargs={'pk':condo_user1.pk})
        self.client.force_authenticate(user=condo_user1)
        response=self.client.patch(url, { 'first_name':'diff name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #INMUEBLE(PROPERTIES) VIEW PERMISSIONS

    def test_condo_can_add_edit_its_properties(self):
        '''Condo can edit its properties'''
        condo_user1 = User.objects.get(username='condo_user1')
        first_property = Inmueble.objects.get(name= '1-a')
        self.client.force_authenticate(user=condo_user1)
        url = reverse('condo_manager:inmueble-detail', kwargs={'pk':first_property.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data= {
            'name':'new name!'
        }
        response=self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_condo_can_not_add_edit_delete_others_properties(self):
        '''Condo does not have access to other condos data resources'''
        first_property = Inmueble.objects.get(name= '1-a')
        condo_user2 = User.objects.get(username ='condo_user2')
        self.client.force_authenticate(user=condo_user2)
        url = reverse('condo_manager:inmueble-detail', kwargs={'pk':first_property.pk})
        response=self.client.get(url)
        assert (response.status_code == status.HTTP_403_FORBIDDEN or status.HTTP_404_NOT_FOUND)

    def test_property_cant_be_created_by_resident(self):
        '''Property can not be created by resident'''
        resident_user= User.objects.get(username='c')
        self.client.force_authenticate(user=resident_user)
        data={}
        url = reverse('condo_manager:inmueble-list')
        response=self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_own_property_can_be_viewed_by_resident(self):
        '''Property can be created by resident'''
        first_property = Inmueble.objects.get(name= '1-a')
        self.client.force_authenticate(user=first_property.resident.user)
        url = reverse('condo_manager:inmueble-detail', kwargs={'pk':first_property.pk})
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_others_property_cant_be_viewed_by_resident(self):
        '''Others property can not be viewed by resident'''
        first_property = Inmueble.objects.get(name= '1-a')
        self.client.force_authenticate(user=first_property.resident.user)
        second_property= Inmueble.objects.get(name='1-b')
        url = reverse('condo_manager:inmueble-detail', kwargs={'pk':second_property.pk})
        response=self.client.get(url)
        self.assertNotEquals(response.status_code, status.HTTP_200_OK)