import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_redirect_link_not_found(client):
    url = reverse('links:redirect_link', kwargs={'slug': 'notexist'})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_redirect_link_inactive(client, link_factory):
    link = link_factory(is_active=False)
    url = reverse('links:redirect_link', kwargs={'slug': link.slug})
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_redirect_link_no_password(client, link_factory):
    link = link_factory(password='')
    url = reverse('links:redirect_link', kwargs={'slug': link.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert response['Location'] == link.original_url


@pytest.mark.django_db
def test_redirect_link_click_count(client, link_factory):
    link = link_factory(password='', is_active=True, click_count=5)
    url = reverse('links:redirect_link', kwargs={'slug': link.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert response['Location'] == link.original_url
    link.refresh_from_db()
    assert link.click_count == 6


@pytest.mark.django_db
def test_redirect_link_password_correct(client, link_factory):
    link = link_factory(password='abc123')
    url = reverse('links:redirect_link', kwargs={'slug': link.slug})
    response = client.post(url, {'password': 'abc123'})
    assert response.status_code == 302
    assert response['Location'] == link.original_url
