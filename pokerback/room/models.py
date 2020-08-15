import random
import uuid
from typing import Optional

from pokerback.poker.objects import PokerGames
from pokerback.room.objects import TableMetadata, Slot
from pokerback.utils.baseobject import BaseRedisObject


class Room(BaseRedisObject):
    room_uuid: str
    room_key: str
    host_user_id: str
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
            table_metadata=TableMetadata(
                game_type=game_type,
                max_slots=max_slots,
                action_seconds_limit=action_seconds_limit,
                slots=[Slot() for x in range(max_slots)],
            ),
        )
        room.save()
        return room_uuid
