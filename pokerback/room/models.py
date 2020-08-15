import random
import uuid
from typing import Optional

from django.db import models

from pokerback.poker.objects import PokerGames
from pokerback.room.objects import (
    GameType,
    RoomStatus,
    Slot,
    TableMetadata,
)
from pokerback.user.models import User
from pokerback.utils.baseobject import BaseRedisObject


class RoomModel(models.Model):
    room_uuid = models.UUIDField(db_index=True)
    room_key = models.CharField(max_length=16, db_index=True)
    host_user = models.ForeignKey(
        User, related_name="host_user", on_delete=models.PROTECT,
    )
    game_type = models.CharField(max_length=64, choices=GameType.choices())
    room_status = models.CharField(max_length=32, choices=RoomStatus.choices())

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True)


class Room(BaseRedisObject):
    room_uuid: str
    room_key: str
    host_user_uuid: str
    room_status: RoomStatus
    table_metadata: TableMetadata

    poker_games: Optional[PokerGames] = None

    object_key_prefix = "room_"

    def get_object_key(self):
        return self.room_uuid

    @classmethod
    def create_room(cls, host_user_id, game_type, max_slots=8, action_seconds_limit=30):
        room_uuid = str(uuid.uuid4())
        room_key = "".join([chr(ord("A") + random.randint(0, 25)) for x in range(5)])

        room = Room(
            room_uuid=room_uuid,
            room_key=room_key,
            host_user_id=host_user_id,
            room_status=RoomStatus.ACTIVE,
            table_metadata=TableMetadata(
                game_type=game_type,
                max_slots=max_slots,
                action_seconds_limit=action_seconds_limit,
                slots=[Slot() for x in range(max_slots)],
            ),
        )
        room.save()
        return room_uuid
