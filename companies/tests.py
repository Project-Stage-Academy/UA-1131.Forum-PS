from rest_framework.test import APITestCase, APIClient
from authentication.models import CustomUser

class CreateCompanyTest(APITestCase):
    def test_create_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('http://127.0.0.1:8000/companies/',{'brand': 'test_brand', 'is_registered': True}, format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_company(self):
        user = CustomUser()
        client = APIClient()
        client.force_authenticate(user=user)
        client.post('http://127.0.0.1:8000/companies/',{'brand': 'test_brand', 'is_registered': True}, format='json')
        response = client.get('http://127.0.0.1:8000/companies/2', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_negative_unauthorized_user(self):
        response = self.client.post('http://127.0.0.1:8000/companies/',{'brand': 'test_brand', 'is_registered': True}, format='json')
        self.assertEqual(response.status_code, 401)