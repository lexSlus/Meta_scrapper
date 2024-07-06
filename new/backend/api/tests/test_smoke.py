from django.urls import reverse


def test_view(client):
    url = reverse("smoke")
    response = client.get(url)
    assert response.status_code == 200
