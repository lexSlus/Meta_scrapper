from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserLoginTests(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(email='active@example.com', password='testpass123', is_active=True)
        self.inactive_user = User.objects.create_user(email='inactive@example.com', password='testpass123',
                                                      is_active=False)

    def test_login_success(self):
        data = {'email': 'active@example.com', 'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_invalid_credentials(self):
        data = {'email': 'active@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials.')

    def test_login_missing_credentials(self):
        data = {'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Please provide both email and password.')

        data = {'email': 'active@example.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Please provide both email and password.')
