from enum import Enum
from typing import List, Optional

from pokerback.utils.baseobject import BaseObject
from pokerback.utils.enums import ModelEnum


class GameType(ModelEnum):
    POKER = "poker"


class SlotStatus(Enum):
    ACTIVE = "active"
    SPECTATE = "spectate"
    EMPTY = "empty"


class Slot(BaseObject):
    player_id: Optional[str] = None
    slot_status: SlotStatus = SlotStatus.EMPTY


class TableMetadata(BaseObject):
    game_type: GameType
    max_slots: int
    slots: List[Slot]
    action_seconds_limit: int


class RoomStatus(ModelEnum):
    ACTIVE = "active"
    CLOSED = "closed"
