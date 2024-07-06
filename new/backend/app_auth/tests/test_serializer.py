from django.test import TestCase
from rest_framework_simplejwt.exceptions import TokenError
from app_auth.models import CompanyUser, Company
from app_auth.serializers import AccountSerializer, AccountSerializerWithToken
from rest_framework_simplejwt.tokens import AccessToken


class SerializerTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'company': self.company
        }
        self.user = CompanyUser.objects.create(**self.user_data)

    def test_account_serializer(self):
        serializer = AccountSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['name'], self.user_data['name'])
        self.assertEqual(data['is_active'], self.user_data['is_active'])
        self.assertEqual(data['company'], self.company.id)

    def test_account_serializer_with_token(self):
        serializer = AccountSerializerWithToken(instance=self.user)
        data = serializer.data
        self.assertIn('token', data)
        self.assertTrue(data['token'])

        try:
            decoded_token = AccessToken(data['token'])
            self.assertEqual(str(decoded_token['user_id']), str(self.user.id))
        except TokenError as e:
            self.fail(f"TokenError raised: {str(e)}")

    def test_serializer_validation(self):
        invalid_data = {**self.user_data, 'email': 'notanemail'}
        serializer = AccountSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
