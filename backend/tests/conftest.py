import pytest

from tests.factories import LinkFactory


@pytest.fixture
def link_factory():
    return LinkFactory
