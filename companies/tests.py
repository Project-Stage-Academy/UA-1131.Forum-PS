from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from authentication.models import CustomUser


class CompanyTestAuthenticatedUser(APITestCase):

    def setUp(self):
        self.company_url = reverse('companies-list-create')
        user = CustomUser.objects.create_user('test@mail.com','Test_password123456')
        self.client = APIClient()
        self.client.force_authenticate(user=user)        
    
    def test_create_company(self):
        response = self.client.post(reverse('companies-list-create'), {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_company(self):
        post_response = self.client.post(self.company_url, {'brand': 'test_brand', 'is_registered': True}, format='json')
        company_id = post_response.data.get('company_id')
        response = self.client.get(f'{self.company_url}{company_id}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_update_company(self):
        response = self.client.post(self.company_url, {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data['company_id']
        response = self.client.patch(f'{self.company_url}{company_id}/', {'brand': 'updated_brand'},
                                format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['brand'], 'updated_brand')

    def test_delete_company(self):
        response = self.client.post(self.company_url, {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data.get('company_id')
        response = self.client.delete(f'{self.company_url}{company_id}/')
        self.assertEqual(response.status_code, 204)

    def test_valid_edrpou(self):
        valid_post_body = {'brand': 'test_brand', 'is_registered': True, 'edrpou': 98756775}
        response = self.client.post(self.company_url, valid_post_body, format='json')
        self.assertEqual(response.status_code, 201)

    def test_valid_phone(self):
        valid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': '+380937777777'}
        response = self.client.post(self.company_url, valid_post_body, format='json')
        self.assertEqual(response.status_code, 201)

    def test_negative_incorrect_edrpou(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'edrpou': 987567}
        response = self.client.post(self.company_url, invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_negative_invalid_phone(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': 'jh0937777777'}
        response = self.client.post(self.company_url, invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_company_with_invalid_data(self):
        response = self.client.post(self.company_url, {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data['company_id']
        response = self.client.patch(f'{self.company_url}{company_id}/', {'edrpou': 'invalid_data'},
                                format='json')
        self.assertEqual(response.status_code, 400)

    def test_get_nonexistent_company(self):
        response = self.client.get(f'{self.company_url}1000', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_create_company_with_invalid_phone_number(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': 'invalid_phone'}
        response = self.client.post(self.company_url, invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)



class CompanyTestUnauthenticatedUser(APITestCase):

    def test_negative_unauthenticated_user(self):
        response = self.client.post(reverse('companies-list-create'), {'brand': 'test_brand', 'is_registered': True},
                                    format='json')
        self.assertEqual(response.status_code, 401)
        

