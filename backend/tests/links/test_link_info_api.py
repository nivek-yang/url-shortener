import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_fetch_page_info_api_success(client, requests_mock):
    url = reverse('links:fetch_page_info_api')
    test_url = 'https://example.com'
    html = """
        <html>
            <head>
                <title>Example Title</title>
                <meta name="description" content="Example description.">
            </head>
            <body></body>
        </html>
    """
    # Mock requests.get to return the above HTML
    requests_mock.get(test_url, text=html)

    response = client.post(
        url, data={'original_url': test_url}, content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert '標題：Example Title' in data['notes']
    assert '描述：Example description.' in data['notes']


@pytest.mark.django_db
def test_fetch_page_info_api_no_url(client):
    url = reverse('links:fetch_page_info_api')
    response = client.post(url, data={}, content_type='application/json')
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert data['message'] == '未提供 URL。'


@pytest.mark.django_db
def test_fetch_page_info_api_request_exception(client, requests_mock):
    url = reverse('links:fetch_page_info_api')
    test_url = 'https://fail.com'
    # Mock requests.get to raise a requests.exceptions.RequestException
    requests_mock.get(test_url, exc=Exception('Connection error'))

    response = client.post(
        url, data={'original_url': test_url}, content_type='application/json'
    )
    assert response.status_code == 500
    data = response.json()
    assert data['success'] is False
    assert data['message'] == '處理時發生錯誤'
