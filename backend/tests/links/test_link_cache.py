
import pytest
from django.core.cache import cache
from django.urls import reverse

from links.models import Link


@pytest.mark.django_db
def test_link_is_cached_after_first_visit(client, link_factory):
    """Test that a link is cached after the first visit."""
    link = link_factory()
    cache.delete(f'link:{link.slug}')  # Ensure cache is clean

    # First visit
    response = client.get(reverse('links:redirect_link', kwargs={'slug': link.slug}))
    assert response.status_code == 302

    # Check that the link is now in the cache
    cached_link = cache.get(f'link:{link.slug}')
    assert cached_link is not None
    assert cached_link['original_url'] == link.original_url


@pytest.mark.django_db
def test_cached_link_is_served_from_cache(client, link_factory, django_assert_num_queries):
    """Test that a cached link is served from the cache on the second visit."""
    link = link_factory()
    # First visit to populate cache
    client.get(reverse('links:redirect_link', kwargs={'slug': link.slug}))

    # Second visit should not hit the database
    with django_assert_num_queries(0):
        response = client.get(reverse('links:redirect_link', kwargs={'slug': link.slug}))
        assert response.status_code == 302


@pytest.mark.django_db
def test_click_count_is_incremented_in_redis(client, link_factory):
    """Test that the click count is incremented in Redis."""
    from links.views import counter_redis

    link = link_factory()
    counter_redis.delete(f'click_count:{link.slug}')  # Ensure counter is clean

    # Visit the link 3 times
    for _ in range(3):
        client.get(reverse('links:redirect_link', kwargs={'slug': link.slug}))

    # Check the click count in Redis
    click_count = counter_redis.get(f'click_count:{link.slug}')
    assert int(click_count) == 3


@pytest.mark.django_db
def test_cache_invalidation_on_link_update(client, link_factory):
    """Test that updating a link invalidates the cache."""
    link = link_factory()
    client.get(reverse('links:redirect_link', kwargs={'slug': link.slug}))  # Populate cache

    # Update the link
    link.original_url = 'https://example.com/updated'
    link.save()

    # Check that the cache is invalidated
    cached_link = cache.get(f'link:{link.slug}')
    assert cached_link is None
