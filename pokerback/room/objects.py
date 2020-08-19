from typing import List, Optional

from pokerback.utils.baseobject import BaseObject
from pokerback.utils.enums import ModelEnum


class GameType(ModelEnum):
    POKER = "poker"


class SlotStatus(ModelEnum):
    ACTIVE = "active"
    SPECTATE = "spectate"
    EMPTY = "empty"


class Slot(BaseObject):
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    slot_status: SlotStatus = SlotStatus.EMPTY


class TableMetadata(BaseObject):
    game_type: GameType
    max_slots: int
    slots: List[Slot]
    action_seconds_limit: int

    def get_active_players(self):
        player_ids = set()
        for slot in self.slots:
            if slot.slot_status == SlotStatus.ACTIVE:
                player_ids.add(slot.player_id)
        return player_ids


class RoomStatus(ModelEnum):
    ACTIVE = "active"
    CLOSED = "closed"
