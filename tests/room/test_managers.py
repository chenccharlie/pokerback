import pytest

from django.core.exceptions import ValidationError

from pokerback.room.managers import RoomManager
from pokerback.room.objects import GameType, RoomStatus


@pytest.mark.django_db
def test_create_room(user):
    room_model = RoomManager.create_room(user, GameType.POKER)
    assert room_model.room_status == str(RoomStatus.ACTIVE)

    room = room_model.load_room()
    assert room.room_key == room_model.room_key
    assert room.table_metadata.max_slots == 8
    assert room.table_metadata.action_seconds_limit == 60


@pytest.mark.django_db
def test_create_room_custom_poker(user):
    room_model = RoomManager.create_room(
        user, GameType.POKER, max_slots=6, action_seconds_limit=30
    )
    assert room_model.room_status == str(RoomStatus.ACTIVE)

    room = room_model.load_room()
    assert room.room_key == room_model.room_key
    assert room.table_metadata.max_slots == 6
    assert room.table_metadata.action_seconds_limit == 30


@pytest.mark.django_db
def test_create_room_unknown_type(user):
    with pytest.raises(ValidationError):
        room_model = RoomManager.create_room(user, "some_game")
