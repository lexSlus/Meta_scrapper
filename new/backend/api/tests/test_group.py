from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from api.models import Group

User = get_user_model()

class GroupViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        self.group = Group.objects.create(fb_id="12345", last_post_id="post123")

    def test_post_group(self):
        url = reverse('groups')
        data = {'fb_id': '67890', 'last_post_id': 'post678'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.get(fb_id='67890').last_post_id, 'post678')

    def test_patch_group(self):
        url = reverse('groups') + '?id=' + str(self.group.id)
        updated_data = {'last_post_id': 'updated_post'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group.refresh_from_db()
        self.assertEqual(self.group.last_post_id, 'updated_post')

    def test_delete_group(self):
        url = reverse('groups') + '?id=' + str(self.group.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=self.group.id)

    def test_error_on_missing_id_for_patch(self):
        url = reverse('groups')
        response = self.client.patch(url, {'last_post_id': 'fail_update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_on_missing_id_for_delete(self):
        url = reverse('groups')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GroupModelTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(fb_id="123456789")

    def test_group_creation(self):
        self.assertEqual(self.group.fb_id, "123456789")
        self.assertEqual(self.group.last_post_id, "")
        self.assertTrue(self.group.is_active)

    def test_group_string_representation(self):
        expected_string = f"{self.group}"
        self.assertEqual(str(self.group), expected_string)

    def test_group_unique_fb_id(self):
        with self.assertRaises(ValidationError):
            new_group = Group(fb_id="123456789")
            new_group.full_clean()

    def test_group_field_lengths(self):
        group = Group(fb_id='1' * 31)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_toggle_group_active_status(self):
        self.group.is_active = False
        self.group.save()
        updated_group = Group.objects.get(id=self.group.id)
        self.assertFalse(updated_group.is_active)