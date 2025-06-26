import factory
from django.utils import timezone

from links.models import Link
from links.utils import generate_unique_slug


class LinkFactory(factory.django.DjangoModelFactory):
    """Factory for creating Link objects with auto-generated slugs."""

    class Meta:
        model = Link

    original_url = factory.Faker('url')
    slug = factory.LazyFunction(generate_unique_slug)
    password = ''
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    expires_at = None
