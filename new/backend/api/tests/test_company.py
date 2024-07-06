from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from api.models import Company

User = get_user_model()


class CompanyViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.company = Company.objects.create(name="Test Company")

    def test_create_company(self):
        initial_count = Company.objects.count()
        url = reverse('company_manage')
        data = {'name': 'New Company'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), initial_count + 1)
        self.assertEqual(Company.objects.get(id=response.data['id']).name, 'New Company')

    def test_patch_company(self):
        url = reverse('company_manage') + '?id=' + str(self.company.id)
        updated_data = {'name': 'Updated Company'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company')

    def test_delete_company(self):
        url = reverse('company_manage') + '?id=' + str(self.company.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Company.DoesNotExist):
            Company.objects.get(id=self.company.id)

    def test_missing_id_on_patch(self):
        url = reverse('company_manage')
        response = self.client.patch(url, {'name': 'Fail Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_id_on_delete(self):
        url = reverse('company_manage')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CompanyModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Example Company")

    def test_create_company(self):
        self.assertTrue(isinstance(self.company, Company))
        self.assertEqual(self.company.name, "Example Company")
        self.assertFalse(self.company.is_staff)
        self.assertTrue(self.company.is_active)

    def test_company_string_representation(self):
        expected_string = f"{self.company.name} - {self.company.id}"
        self.assertEqual(str(self.company), expected_string)

    def test_company_unique_id(self):
        another_company = Company.objects.create(name="Another Company")
        self.assertNotEqual(self.company.id, another_company.id)

    def test_company_field_max_length(self):
        with self.assertRaises(ValidationError):
            long_name_company = Company(name='x' * 71)
            long_name_company.full_clean()

    def test_toggle_company_active_status(self):
        self.company.is_active = False
        self.company.save()
        updated_company = Company.objects.get(id=self.company.id)
        self.assertFalse(updated_company.is_active)
