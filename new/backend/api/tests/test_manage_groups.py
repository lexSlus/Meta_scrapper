from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.models import Group


class GroupViewSetTestCase(APITestCase):
    client = APIClient()

    def setUp(self):
        self.group1 = Group.objects.create(fb_id="fb001", last_post_id="post001")
        self.group2 = Group.objects.create(fb_id="fb002", last_post_id="post002")

    def test_batch_create_groups(self):
        url = reverse('group-batch-create')
        data = [
            {'fb_id': 'fb003', 'last_post_id': 'post003'},
            {'fb_id': 'fb004', 'last_post_id': 'post004'}
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 4)  # Check if now there are 4 groups

    def test_batch_update_groups(self):
        url = reverse('group-batch-update')
        data = [
            {'id': str(self.group1.id), 'last_post_id': 'new_post001'},
            {'id': str(self.group2.id), 'last_post_id': 'new_post002'}
        ]
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group1.refresh_from_db()
        self.group2.refresh_from_db()
        self.assertEqual(self.group1.last_post_id, 'new_post001')
        self.assertEqual(self.group2.last_post_id, 'new_post002')

    def test_batch_delete_groups(self):
        url = reverse('group-batch-delete')
        data = {'ids': [str(self.group1.id), str(self.group2.id)]}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Group.objects.count(), 0)
