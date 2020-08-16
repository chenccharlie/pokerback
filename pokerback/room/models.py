from typing import Optional

from django.db import models
from django.db.models.constraints import UniqueConstraint

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
    closed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def _default_max_slots(self, game_type):
        max_slots = {
            GameType.POKER.value: 8,
        }
        return max_slots[game_type]

    def _default_action_seconds_limit(self, game_type):
        action_seconds_limit = {
            GameType.POKER.value: 60,
        }
        return action_seconds_limit[game_type]

    def init_room(self, **kwargs):
        max_slots = kwargs.pop("max_slots", self._default_max_slots(self.game_type))
        action_seconds_limit = kwargs.pop(
            "action_seconds_limit", self._default_action_seconds_limit(self.game_type)
        )

        room = Room(
            room_uuid=str(self.room_uuid),
            room_key=self.room_key,
            host_user_uuid=str(self.host_user.uuid),
            room_status=RoomStatus.ACTIVE,
            table_metadata=TableMetadata(
                game_type=GameType(self.game_type),
                max_slots=max_slots,
                action_seconds_limit=action_seconds_limit,
                slots=[Slot() for x in range(max_slots)],
            ),
        )
        room.save()
        return room

    def load_room(self):
        return Room.load(str(self.room_uuid))

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["room_key"],
                condition=models.Q(room_status="active"),
                name="unique_active_key",
            ),
            UniqueConstraint(
                fields=["host_user"],
                condition=models.Q(room_status="active"),
                name="unique_active_per_user",
            ),
        ]


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
