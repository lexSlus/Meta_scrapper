from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from api.models import Broker, Company
from app_auth.models import CompanyUser


class BrokerManagementTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.company = Company.objects.create(name="Test Company", is_staff=False)

        self.company_user = CompanyUser.objects.create_user(
            email="user@test.com",
            password="password",
            company=self.company
        )

        self.broker1 = Broker.objects.create(
            fb_id="fb001",
            is_activated=True,
            fb_link="http://link1.com",
            # user=self.company_user,
            company=self.company
        )
        self.broker2 = Broker.objects.create(
            fb_id="fb002",
            is_activated=False,
            fb_link="http://link2.com",
            # user=self.company_user,
            company=self.company
        )

    def test_batch_update_brokers_success(self):
        url = reverse('broker-batch-update')
        data = [
            {'id': self.broker1.id, 'is_activated': False, 'fb_link': 'http://updatedlink1.com'},
            {'id': self.broker2.id, 'is_activated': True, 'fb_link': 'http://updatedlink2.com'}
        ]
        self.client.login(email='user@test.com', password='password')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.broker1.refresh_from_db()
        self.broker2.refresh_from_db()
        self.assertFalse(self.broker1.is_activated)
        self.assertTrue(self.broker2.is_activated)

    def test_batch_update_brokers_failure(self):
        url = reverse('broker-batch-update')
        data = [{'id': 9999, 'is_activated': True}]
        self.client.login(email='user@test.com', password='password')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_batch_delete_brokers_success(self):
        url = reverse('broker-batch-delete')
        data = {'ids': [self.broker1.id, self.broker2.id]}
        self.client.login(email='user@test.com', password='password')
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Broker.objects.count(), 0)

    def test_batch_delete_brokers_failure(self):
        url = reverse('broker-batch-delete')
        data = {'ids': [9999]}
        self.client.login(email='user@test.com', password='password')
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
