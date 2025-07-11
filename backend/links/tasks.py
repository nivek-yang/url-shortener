from celery import shared_task
from django.db.models import F

from .models import Link
from .views import counter_redis


@shared_task
def sync_click_counts():
    """
    A Celery task that syncs click counts from Redis to the main database.
    This task is scheduled to run periodically by Celery Beat.
    """
    click_keys = counter_redis.keys('click_count:*')

    if not click_keys:
        return 'No click counts in Redis to sync.'

    # Decode keys and extract slugs
    slugs = [key.decode('utf-8').split(':')[-1] for key in click_keys]

    # Use a Redis pipeline for atomic and efficient operations
    with counter_redis.pipeline() as pipe:
        for key in click_keys:
            pipe.get(key)
            pipe.set(key, 0)
        redis_results = pipe.execute()

    click_counts = redis_results[::2]

    # Create a mapping from slug to its corresponding click count to add
    slug_to_count_map = {
        slug: int(count) if count else 0 for slug, count in zip(slugs, click_counts)
    }

    # Fetch all relevant links from the database in a single query
    links_from_db = Link.objects.filter(slug__in=slugs)

    # Create a slug -> pk mapping for efficient lookup
    slug_to_pk_map = {link.slug: link.pk for link in links_from_db}

    links_to_update = []
    for slug, count_to_add in slug_to_count_map.items():
        if count_to_add > 0 and slug in slug_to_pk_map:
            link = Link(pk=slug_to_pk_map[slug])  # Set the primary key
            link.click_count = F('click_count') + count_to_add
            links_to_update.append(link)

    if links_to_update:
        Link.objects.bulk_update(links_to_update, ['click_count'])
        return f'Successfully synced {len(links_to_update)} link click counts.'

    return 'No updates were necessary.'
