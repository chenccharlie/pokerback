from typing import Optional

from pokerback.room.models import Room
from pokerback.room.objects import GameType
from pokerback.utils.baseobject import BaseObject


class PlayerRetrieveRoomResponse(BaseObject):
    room: Room


class PlayerSigninRequest(BaseObject):
    room_key: str
    name: str


class PlayerSitRoomRequest(BaseObject):
    slot_idx: int
