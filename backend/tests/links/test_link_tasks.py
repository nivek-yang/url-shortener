import pytest
from django.test import override_settings

from links.tasks import sync_click_counts
from links.views import counter_redis


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_sync_click_counts_task(link_factory):
    """
    Test the sync_click_counts Celery task to ensure it correctly
    syncs counts from Redis to the database and resets the Redis counter.
    """
    # 1. Prepare test data
    # Create two links with existing click counts in the database
    link1 = link_factory(slug='link-1', click_count=10)
    link2 = link_factory(slug='link-2', click_count=5)

    # Manually set some new click counts in Redis
    counter_redis.set(f'click_count:{link1.slug}', 3)
    counter_redis.set(f'click_count:{link2.slug}', 7)
    # This one should be ignored as it has no new clicks
    counter_redis.set('click_count:link-3-no-clicks', 0)

    # 2. Execute the task
    # In Eager mode, this runs the function synchronously
    sync_click_counts.delay()

    # 3. Verify database state
    # Refresh the objects from the database to get the updated values
    link1.refresh_from_db()
    link2.refresh_from_db()

    # The new count should be the sum of the old DB count and the Redis count
    assert link1.click_count == 13  # 10 (db) + 3 (redis)
    assert link2.click_count == 12  # 5 (db) + 7 (redis)

    # 4. Verify Redis state
    # The counters in Redis should be reset to 0
    assert int(counter_redis.get(f'click_count:{link1.slug}')) == 0
    assert int(counter_redis.get(f'click_count:{link2.slug}')) == 0
    # The key with 0 clicks should also be reset
    assert int(counter_redis.get('click_count:link-3-no-clicks')) == 0
