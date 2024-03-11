from unittest import mock
from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from forum import settings
from forum.managers import TokenManager

from .models import Company, CompanyAndUserRelation, CustomUser


class AuthenticationUserApiTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(email='test2@gmail.com', password='password123')
        self.user2 = CustomUser.objects.create_user(email='test3@gmail.com', password='password123')
        self.user3 = CustomUser.objects.create_user(email='test4@gmail.com', password='password123')
        self.company = Company.objects.create(brand='Pepsi')

    def _authenticate_user(self, refresh_token):
        jwt_token = f'Bearer {refresh_token.access_token}'
        self.client.credentials(HTTP_AUTHORIZATION=jwt_token)

    @patch('authentication.utils.Utils.send_verification_email')
    def test_register_user(self, mock_send_verification_email):
        data_to_send = {'email': 'register@mail.com',
                        'password': 'Test_password123456',
                        'password2': 'Test_password123456',
                        'first_name': 'TestName',
                        'surname': 'TestSurname',
                        'phone_number': '+380676342542'}
        returned_response = self.client.post(reverse('auth_register'), data_to_send, format='json')

        response_to_expect = {
            "email": "register@mail.com",
            "first_name": "TestName",
            "surname": "TestSurname",
            "phone_number": "+380676342542"
        }
        self.assertEqual(returned_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(returned_response.data, response_to_expect)
        mock_send_verification_email.assert_called_once()

    def test_register_user_invalid_data(self):
        data = {
            'email': 'register@mail.com',
            'password': 'Test_password123456',
        }
        returned_response = self.client.post(reverse('auth_register'), data, format='json')

        self.assertEqual(returned_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {'email': 'test2@gmail.com', 'password': 'password123'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)

    def test_login_user_not_found(self):
        data = {'email': 'nonexistent@example.com', 'password': 'password123'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_invalid_credentials(self):
        data = {'email': 'test2@gmail.com', 'password': 'wrongpassword'}
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        refresh_token = TokenManager.generate_refresh_token_for_user(self.user)
        self._authenticate_user(refresh_token)
        data = {'refresh_token': str(refresh_token)}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_invalid_token(self):
        data = {'refresh_token': 'my_magic_token'}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('authentication.utils.Utils.send_password_reset_email')
    @patch('forum.managers.TokenManager.generate_access_token_for_user')
    def test_password_recovery_success(self, mock_generate_access_token_for_user, mock_send_password_reset_email):
        mock_access_token = 'jwt_token'
        mock_generate_access_token_for_user.return_value = mock_access_token

        response = self.client.post(reverse('password_recovery'), {'email': self.user2.email}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset email sent successfully')
        mock_send_password_reset_email.assert_called_once_with(self.user2.email,
                                                               settings.FRONTEND_URL +
                                                               reverse('password_reset', args=(mock_access_token,)))

    def test_password_recovery_not_found_email(self):
        response = self.client.post(reverse('password_recovery'), {'email': 'nonexistent@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('forum.managers.TokenManager.get_access_payload')
    def test_password_reset_success(self, mock_get_access_payload):
        jwt_token = 'mock_jwt_token'
        password = 'new_password123!ABC'
        mock_get_access_payload.return_value = {'user_id': self.user3.user_id}

        response = self.client.post(reverse('password_reset', args=(jwt_token,)),
                                    {'password': password, 'password2': password}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset successfully')
        self.user3.refresh_from_db()
        self.assertTrue(self.user3.check_password(password))

    @patch('forum.managers.TokenManager.get_access_payload')
    def test_password_reset_short_password(self, mock_get_access_payload):
        jwt_token = 'mock_jwt_token'
        password = '123'
        mock_get_access_payload.return_value = {'user_id': self.user3.user_id}

        response = self.client.post(reverse('password_reset', args=(jwt_token,)),
                                    {'password': password, 'password2': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('forum.managers.TokenManager.get_access_payload')
    def test_verify_email_success(self, mock_get_access_payload):
        mock_token = 'mock_token'
        mock_get_access_payload.return_value = {'user_id': self.user3.user_id}
        response = self.client.get(reverse('email_verify', args=(mock_token,)), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'Successfully Verified')
        self.user3.refresh_from_db()
        self.assertTrue(self.user3.is_verified)

    def test_verify_email_invalid_token(self):
        mock_token = None
        response = self.client.get(reverse('email_verify', args=(mock_token,)), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Token is invalid or expired')

    def test_relate_user_to_company_success(self):
        CompanyAndUserRelation.objects.create(user_id=self.user, company_id=self.company)

        refresh_token = TokenManager.generate_refresh_token_for_user(self.user)
        self._authenticate_user(refresh_token)

        response = self.client.post(reverse('relate'), {'company_id': self.company.company_id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue(response.data['access'].startswith('Bearer '))

    def test_relate_user_to_company_no_relation(self):
        refresh_token = TokenManager.generate_refresh_token_for_user(self.user)
        self._authenticate_user(refresh_token)

        response = self.client.post(reverse('relate'), {'company_id': self.company.company_id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'You have no access to this company.')

    @patch('authentication.utils.Utils.send_verification_email')
    def test_user_password_update_success(self, mock_send_verification_email: mock.MagicMock):
        url = reverse('user_details', args=(self.user.user_id,))
        data = {
            'email': 'new_email@example.com',
            'first_name': 'Arseniy',
            'surname': 'LikePython',
            'phone_number': '+38987654321'
        }
        refresh_token = TokenManager.generate_refresh_token_for_user(self.user)
        self._authenticate_user(refresh_token=refresh_token)

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(response.data['email'], 'new_email@example.com')
        self.assertEqual(response.data['first_name'], 'Arseniy')
        self.assertEqual(response.data['surname'], 'LikePython')
        self.assertEqual(response.data['phone_number'], '+38987654321')
        mock_send_verification_email.assert_called_once()

    def test_user_password_update_invalid_data(self):
        url = reverse('user_details', args=(self.user.user_id,))
        data = {
            'email': 'Nothing',
            'first_name': 'will',
            'surname': 'work',
            'phone_number': 'unless you do'
        }
        refresh_token = TokenManager.generate_refresh_token_for_user(self.user)
        self._authenticate_user(refresh_token=refresh_token)

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'], ['Enter a valid email address.'])
