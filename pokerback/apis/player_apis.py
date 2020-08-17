from typing import Optional

from pokerback.room.models import Room
from pokerback.room.objects import GameType
from pokerback.utils.baseobject import BaseObject


class PlayerRetrieveRoomRequest(BaseObject):
    room_key: str


class PlayerRetrieveRoomResponse(BaseObject):
    room: Room


class PlayerJoinRoomRequest(BaseObject):
    room_key: str
    slot_idx: int
