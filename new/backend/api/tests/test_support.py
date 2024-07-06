from unittest.mock import patch, Mock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from api.models import SupportRequest


class SupportRequestModelTestCase(TestCase):
    def setUp(self):
        self.support_request = SupportRequest.objects.create(
            contact_email="user@example.com",
            topic="Test Support Request",
            details="Need help with testing."
        )

    def test_model_str(self):
        self.assertEqual(str(self.support_request), "Test Support Request by user@example.com")


class SupportRequestAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse('support_api')
        self.valid_payload = {
            'contact_email': 'user@example.com',
            'topic': 'Urgent Help Needed',
            'details': 'Please assist with urgent issue.'
        }
        self.invalid_payload = {
            'contact_email': 'not-an-email',
            'topic': 'Bad Request',
            'details': ''
        }

    @patch('api.views.support.send_support_email')
    @patch('boto3.client')
    def test_create_support_request_with_valid_data(self, mock_boto_client, mock_send_email):
        mock_ses_client = Mock()
        mock_boto_client.return_value = mock_ses_client
        mock_ses_client.send_email.return_value = {'MessageId': 'fake-id'}

        response = self.client.post(self.url, self.valid_payload)
        print("Test Response:", response.data)  # Debug output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SupportRequest.objects.exists())

        try:
            mock_send_email.assert_called_once()
        except AssertionError:
            print("send_email was not called")
            raise

    def test_create_support_request_with_invalid_data(self):
        response = self.client.post(self.url, self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SupportRequest.objects.exists())

    @patch('api.send_email.send_support_email')
    def test_create_support_request_without_email(self, mock_send_email):
        payload = self.valid_payload.copy()
        del payload['contact_email']
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SupportRequest.objects.exists())
        mock_send_email.assert_not_called()
