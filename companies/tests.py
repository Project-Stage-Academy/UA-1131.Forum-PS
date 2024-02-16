from rest_framework.test import APITestCase, APIClient

from authentication.models import CustomUser


class CreateCompanyTest(APITestCase):
    def test_create_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True}, format='json')
        response = client.get('http://127.0.0.1:8000/companies/2', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_update_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data['company_id']
        response = client.patch(f'http://127.0.0.1:8000/companies/{company_id}/', {'brand': 'updated_brand'},
                                format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['brand'], 'updated_brand')

    def test_delete_company(self):
        client = APIClient()
        response = client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data.get('id')
        client.logout()
        response = client.delete(f'http://127.0.0.1:8000/companies/{company_id}/')
        self.assertEqual(response.status_code, 404)

    def test_valid_edrpou(self):
        valid_post_body = {'brand': 'test_brand', 'is_registered': True, 'edrpou': 98756775}
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', valid_post_body, format='json')
        self.assertEqual(response.status_code, 201)

    def test_valid_phone(self):
        valid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': '+380937777777'}
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', valid_post_body, format='json')
        self.assertEqual(response.status_code, 201)

    def test_negative_unauthorized_user(self):
        response = self.client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                                    format='json')
        self.assertEqual(response.status_code, 401)

    def test_negative_incorrect_edrpou(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'edrpou': 987567}
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_negative_invalid_phone(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': 'jh0937777777'}
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_company_with_invalid_data(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        company_id = response.data['company_id']
        response = client.patch(f'http://127.0.0.1:8000/companies/{company_id}/', {'edrpou': 'invalid_data'},
                                format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_company_without_authentication(self):
        client = APIClient()
        response = client.post('http://127.0.0.1:8000/companies/', {'brand': 'test_brand', 'is_registered': True},
                               format='json')
        self.assertEqual(response.status_code, 401)

    def test_get_nonexistent_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('http://127.0.0.1:8000/companies/1000', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_create_company_with_invalid_phone_number(self):
        invalid_post_body = {'brand': 'test_brand', 'is_registered': True, 'contact_phone': 'invalid_phone'}
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/', invalid_post_body, format='json')
        self.assertEqual(response.status_code, 400)



