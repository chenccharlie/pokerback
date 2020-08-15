from enum import Enum
from typing import List, Optional

from pokerback.utils.baseobject import BaseObject


class GameType(Enum):
    POKER = 1


class SlotStatus(Enum):
    ACTIVE = 1
    SPECTATE = 2
    EMPTY = 3


class Slot(BaseObject):
    player_id: Optional[str] = None
    slot_status: SlotStatus = SlotStatus.EMPTY


class TableMetadata(BaseObject):
    game_type: GameType
    max_slots: int
    slots: List[Slot]
    action_seconds_limit: int
