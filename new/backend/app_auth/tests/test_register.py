from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError

from app_auth.models import CompanyUser, Company
from rest_framework_simplejwt.tokens import AccessToken


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.company = Company.objects.create(name="Test Company")
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'company': self.company.id
        }

    def test_register_user_success(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_register_user_missing_fields(self):
        data = self.user_data.copy()
        del data['name']
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Missing required fields')

    def test_register_user_duplicate_email(self):
        self.client.post(self.url, self.user_data, format='json')
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Account with this email already exists')

    def test_register_user_with_company(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('company' in response.data)

    def test_token_generation(self):
        response = self.client.post(self.url, self.user_data, format='json')
        user = CompanyUser.objects.get(email=self.user_data['email'])
        actual_token = response.data['token']

        try:
            decoded_token = AccessToken(actual_token)
            self.assertEqual(str(decoded_token['user_id']), str(user.id))
        except TokenError as e:
            self.fail(f"TokenError raised: {str(e)}")

        self.assertEqual(decoded_token['user_id'], user.id)
