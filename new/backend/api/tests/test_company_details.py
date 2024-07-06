from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyBrokersGroupsViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)

        self.company = Company.objects.create(name="Test Company")

    def test_get_company_details_success(self):
        url = reverse('company-brokers-groups')
        response = self.client.get(url, {'company_id': str(self.company.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], 'Test Company')

    def test_missing_company_id(self):
        url = reverse('company-brokers-groups')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.data, {"error": "Missing company_id in request"})
