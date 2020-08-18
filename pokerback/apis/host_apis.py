from typing import Optional

from pokerback.room.models import Room
from pokerback.room.objects import GameType
from pokerback.utils.baseobject import BaseObject


class HostCreatePokerRoomRequest(BaseObject):
    small_blind: Optional[int] = None
    init_token: Optional[int] = None


class HostCreateRoomRequest(BaseObject):
    game_type: GameType
    max_slots: Optional[int] = None
    action_limit_seconds: Optional[int] = None
    poker_request: Optional[HostCreatePokerRoomRequest] = None


class HostRetrieveRoomResponse(BaseObject):
    room: Room
