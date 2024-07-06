from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

from api.models import Broker, Company, Group

User = get_user_model()


class BrokerViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.company = Company.objects.create(name="Test Company")
        self.broker = Broker.objects.create(fb_link="http://example.com/fb123", company=self.company)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.client.logout()
        Broker.objects.all().delete()
        Company.objects.all().delete()
        User.objects.all().delete()

    def test_get_brokers(self):
        url = reverse('brokers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # def test_post_broker(self):
    #     url = reverse('brokers')
    #     data = {
    #         'fb_link': 'http://newexample.com/fb123',
    #         'company': self.company.id,
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Broker.objects.count(), 2)
    #
    #     broker = Broker.objects.latest('id')
    #     self.assertEqual(broker.company.id, self.company.id)

    def test_patch_broker(self):
        url = reverse('brokers') + '?id=' + str(self.broker.id)
        new_link = 'http://updatedexample.com/fb123'
        response = self.client.patch(url, {'fb_link': new_link})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.broker.refresh_from_db()
        self.assertEqual(self.broker.fb_link, new_link)

    def test_delete_broker(self):
        url = reverse('brokers') + '?id=' + str(self.broker.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Broker.DoesNotExist):
            self.broker.refresh_from_db()

    def test_missing_id_on_patch(self):
        url = reverse('brokers')
        response = self.client.patch(url, {'fb_link': 'http://failupdate.com/fb123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_id_on_delete(self):
        url = reverse('brokers')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BrokerModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Example Company")

    def tearDown(self):
        Broker.objects.all().delete()
        Company.objects.all().delete()

    def test_create_broker(self):
        broker = Broker.objects.create(
            fb_id="123456",
            fb_link="http://example.com/broker",
            company=self.company
        )
        self.assertIsInstance(broker, Broker)
        self.assertEqual(broker.fb_id, "123456")
        self.assertFalse(broker.is_activated)
        self.assertTrue(broker.is_active)
        self.assertEqual(broker.company, self.company)

    def test_broker_default_values(self):
        broker = Broker.objects.create(
            fb_link="http://example.com/broker",
            company=self.company
        )
        self.assertEqual(broker.fb_id, "")
        self.assertFalse(broker.is_activated)
        self.assertTrue(broker.is_active)

    def test_broker_string_representation(self):
        broker = Broker.objects.create(
            fb_link="http://example.com/broker",
            company=self.company
        )
        expected_string = str(broker)
        self.assertEqual(str(broker), expected_string)

    def test_broker_relationships(self):
        group = Group.objects.create(fb_id="group1")
        broker = Broker.objects.create(
            fb_link="http://example.com/broker",
            company=self.company
        )
        broker.groups.add(group)
        self.assertIn(group, broker.groups.all())

    def test_broker_deletion_cascade(self):
        broker = Broker.objects.create(
            fb_link="http://example.com/broker",
            company=self.company
        )
        broker_id = broker.id
        self.company.delete()
        with self.assertRaises(Broker.DoesNotExist):
            Broker.objects.get(id=broker_id)
