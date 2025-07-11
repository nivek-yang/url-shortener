import os

import pytest
import redis
from django.core.cache import cache

from tests.factories import LinkFactory


@pytest.fixture
def link_factory():
    return LinkFactory


@pytest.fixture(autouse=True)
def clear_redis_cache():
    """
    A fixture to automatically clear all Redis caches before each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    # Clear the default cache (DB 0) used by django-redis
    cache.clear()

    # Clear the counter cache (DB 1) by connecting directly
    counter_redis = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        db=1,  # Ensure we are flushing the correct database
    )
    counter_redis.flushdb()
