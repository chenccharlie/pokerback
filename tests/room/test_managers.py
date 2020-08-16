import pytest

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import GameType, RoomStatus


@pytest.mark.django_db
def test_create_room(user):
    room_model = RoomManager.create_room(user, GameType.POKER)
    assert room_model.room_status == str(RoomStatus.ACTIVE)

    room = room_model.load_room()
    assert room.room_key == room_model.room_key
    assert room.table_metadata.max_slots == 8
    assert room.table_metadata.action_seconds_limit == 60
    assert room.poker_games.game_metadata.small_blind == 10


@pytest.mark.django_db
def test_create_room_custom_poker(user):
    room_model = RoomManager.create_room(
        user, GameType.POKER, max_slots=6, action_seconds_limit=30, small_blind=20,
    )
    assert room_model.room_status == str(RoomStatus.ACTIVE)

    room = room_model.load_room()
    assert room.room_key == room_model.room_key
    assert room.table_metadata.max_slots == 6
    assert room.table_metadata.action_seconds_limit == 30
    assert room.poker_games.game_metadata.small_blind == 20


@pytest.mark.django_db
def test_create_room_unknown_type(user):
    with pytest.raises(ValidationError):
        room_model = RoomManager.create_room(user, "some_game")


@pytest.mark.django_db
def test_create_room_dup_active(user):
    room_model = RoomManager.create_room(user, GameType.POKER)
    with pytest.raises(IntegrityError):
        new_room_model = RoomManager.create_room(user, GameType.POKER)

    room_model.room_status = RoomStatus.CLOSED
    room_model.save()

    new_room_model = RoomManager.create_room(user, GameType.POKER)
    assert room_model.room_uuid != new_room_model.room_uuid
    assert RoomModel.objects.filter(host_user=user).count() == 2
