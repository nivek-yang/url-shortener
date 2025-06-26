# test link factory

import pytest
from django.utils import timezone


# Factory 是否產出合法資料
@pytest.mark.django_db
def test_link_factory_is_valid(link_factory):
    """Test that the link factory produces valid Link objects."""
    link = link_factory()
    assert link.pk is not None
    assert link.original_url.startswith('http://') or link.original_url.startswith(
        'https://'
    )
    assert isinstance(link.slug, str)
    assert len(link.slug) == 6
    assert link.is_active is True
    assert link.created_at.tzinfo is not None
    assert link.created_at is not None
    assert link.expires_at is None


# Factory 欄位型別與格式檢查（包含必填欄位）
@pytest.mark.django_db
def test_link_model_fields(link_factory):
    """Test that the link factory produces Link objects with correct field types and formats."""
    link = link_factory()

    # Check field types
    assert isinstance(link.original_url, str)
    assert isinstance(link.slug, str)
    assert isinstance(link.password, str)
    assert isinstance(link.is_active, bool)
    assert isinstance(link.created_at, timezone.datetime)
    assert link.expires_at is None or isinstance(link.expires_at, timezone.datetime)

    # Check required fields
    assert link.original_url != ''
    assert link.slug != ''
