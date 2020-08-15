import pytest
from uuid import uuid4

from pokerback.user.models import User


@pytest.fixture
def user(uuid=None):
    if uuid is None:
        uuid = uuid4()

    return User.objects.create(uuid=uuid)
