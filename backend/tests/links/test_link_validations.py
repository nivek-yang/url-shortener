import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from links.constants import (
    SLUG_DUPLICATE_ERROR,
    SLUG_MAX_LENGTH_ERROR,
    URL_INVALID_ERROR,
)
from links.models import Link


@pytest.mark.django_db
def test_link_slug_validation(link_factory):
    """Test that a custom slug must be unique."""
    link_factory(slug='custom-slug')
    with pytest.raises(IntegrityError):
        link_factory(slug='custom-slug')


@pytest.mark.django_db
def test_link_slug_generation(link_factory):
    """Test that a link without a custom slug generates a unique slug."""
    link1 = link_factory(slug=None)
    assert len(link1.slug) == 6


@pytest.mark.django_db
def test_link_slug_uniqueness_after_save(link_factory):
    """Test that the slug remains unique after saving."""
    link_factory(slug='unique-slug')

    # Attempt to save a link with the same slug
    with pytest.raises(IntegrityError):
        link_factory(slug='unique-slug')


@pytest.mark.django_db
def test_link_slug_with_special_characters(link_factory):
    """Test that slugs with special characters are slugified correctly."""
    link = link_factory(slug='Custom Slug!@#')
    assert link.slug == 'custom-slug'
    assert len(link.slug) <= 50


@pytest.mark.django_db
def test_link_slug_blank(link_factory):
    """Test that a blank slug generates a unique slug."""
    link = link_factory(slug='')
    assert len(link.slug) == 6
    assert link.slug.isalnum()


@pytest.mark.django_db
def test_link_slug_max_length(link_factory):
    """Test that the slug does not exceed the maximum length and raises a custom error."""
    with pytest.raises(ValidationError) as exc_info:
        link = link_factory.build(slug='a' * 51)
        link.full_clean()
    assert SLUG_MAX_LENGTH_ERROR in str(exc_info.value)


@pytest.mark.django_db
def test_link_invalid_url(link_factory):
    """Test that an invalid URL raises a validation error."""
    with pytest.raises(ValidationError) as exc_info:
        link = link_factory.build(original_url='invalid-url')
        link.full_clean()
    assert URL_INVALID_ERROR in str(exc_info.value)


@pytest.mark.django_db
def test_link_password_max_length(link_factory):
    """Test that the password does not exceed the maximum length and raises a custom error."""
    with pytest.raises(ValidationError) as exc_info:
        link = link_factory.build(password='a' * 65)
        link.full_clean()
    assert 'exceeds maximum length of 64 characters' in str(exc_info.value)