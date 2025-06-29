import pytest
from django.contrib.auth.hashers import check_password
from django.urls import reverse

from links.constants import (
    CREATED_LINK_SUCCESS,
    JSON_PARSE_ERROR,
    ORIGINAL_URL_REQUIRED_ERROR,
    PASSWORD_MAX_LENGTH_ERROR,
    SLUG_DUPLICATE_ERROR,
    SLUG_MAX_LENGTH_ERROR,
    URL_INVALID_ERROR,
)
from links.models import Link


@pytest.mark.django_db
def test_link_shortener_api(client):
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'https://example.com',
        'slug': 'pytest-slug',
        'password': 'pytest123',
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 201
    resp_json = response.json()
    assert resp_json['success'] is True
    assert resp_json['message'] == CREATED_LINK_SUCCESS
    assert resp_json['short_url'].endswith('/pytest-slug')
    assert resp_json['original_url'].startswith('https://example.com')

    # 驗證資料庫有建立
    link = Link.objects.get(slug='pytest-slug')
    assert link.original_url.startswith('https://example.com')
    assert link.password != 'pytest123'
    assert check_password('pytest123', link.password)


@pytest.mark.django_db
def test_link_shortener_api_json_parse_error(client):
    url = reverse('links:link_shortener_api')
    data = 'not-a-json-string'
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == JSON_PARSE_ERROR


@pytest.mark.django_db
def test_link_shortener_api_missing_url(client):
    url = reverse('links:link_shortener_api')
    data = {'slug': 'pytest-slug2'}
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == ORIGINAL_URL_REQUIRED_ERROR


@pytest.mark.django_db
def test_link_shortener_api_duplicate_slug(client, link_factory):
    # 先建立一個 slug
    link_factory(slug='dupeslug')
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'https://example.com',
        'slug': 'dupeslug',
        'password': 'pytest123',
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == SLUG_DUPLICATE_ERROR


@pytest.mark.django_db
def test_link_shortener_api_slug_too_long(client):
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'https://example.com',
        'slug': 'a' * 51,  # 超過 50 字元
        'password': 'pytest123',
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == SLUG_MAX_LENGTH_ERROR


@pytest.mark.django_db
def test_link_shortener_api_invalid_url(client):
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'not-a-url',
        'slug': 'validslug',
        'password': 'pytest123',
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == URL_INVALID_ERROR


@pytest.mark.django_db
def test_link_shortener_api_password_too_long(client):
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'https://example.com',
        'slug': 'validslug2',
        'password': 'a' * 65,  # 超過 64 字元
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['success'] is False
    assert resp_json['message'] == PASSWORD_MAX_LENGTH_ERROR


@pytest.mark.django_db
def test_link_shortener_api_blank_slug(client):
    url = reverse('links:link_shortener_api')
    data = {
        'original_url': 'https://example.com',
        'slug': '',
        'password': 'pytest123',
    }
    response = client.post(url, data=data, content_type='application/json')
    assert response.status_code == 201  # 應該允許自動產生 slug
    resp_json = response.json()
    assert resp_json['original_url'].startswith('https://example.com')
