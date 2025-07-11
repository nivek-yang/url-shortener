import os

import redis
from django.core.cache import caches

# Get the default cache (for links)
link_cache = caches['default']

# Create a separate Redis client for counters
counter_redis = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, db=1
)
