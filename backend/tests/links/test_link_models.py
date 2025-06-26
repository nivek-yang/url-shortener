import pytest

from links.models import Link


@pytest.mark.django_db
def test_link_create(link_factory):
    """Test that a link can be created using the factory."""
    link = link_factory()
    assert link.pk is not None
    assert link.original_url.startswith('http://') or link.original_url.startswith(
        'https://'
    )
    assert len(link.slug) == 6
    assert link.is_active is True
    assert link.created_at is not None
    assert link.expires_at is None


@pytest.mark.django_db
def test_link_read(link_factory):
    """Test that a link can be read from the database."""
    link = link_factory()
    fetched_link = Link.objects.get(pk=link.pk)
    assert fetched_link.original_url == link.original_url
    assert fetched_link.slug == link.slug
    assert fetched_link.is_active == link.is_active
    assert fetched_link.created_at == link.created_at
    assert fetched_link.expires_at == link.expires_at


@pytest.mark.django_db
def test_link_update(link_factory):
    """Test that a link can be updated."""
    link = link_factory()

    # Update data
    new_url = 'https://example.com/updated'
    link.original_url = new_url
    link.slug = 'updated-slug'
    link.password = 'newpassword'

    link.save()

    updated_link = Link.objects.get(pk=link.pk)
    assert updated_link.original_url == new_url
    assert updated_link.slug == 'updated-slug'
    assert updated_link.password == 'newpassword'


@pytest.mark.django_db
def test_link_delete(link_factory):
    """Test that a link can be deleted."""
    link = link_factory()
    link_pk = link.pk
    link.delete()

    with pytest.raises(Link.DoesNotExist):
        Link.objects.get(pk=link_pk)
