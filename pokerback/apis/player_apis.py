from typing import Optional, List

from pokerback.poker.objects import Card, PlayerStateResponse
from pokerback.poker.player_apis import PokerAction
from pokerback.room.managers import get_game_manager
from pokerback.room.models import Room
from pokerback.room.objects import GameType, SlotStatus
from pokerback.utils.baseobject import BaseObject


class PlayerRetrieveRoomResponse(BaseObject):
    name: str
    room_key: str
    game_type: GameType
    slot_idx: Optional[int] = None
    available_slots: List[int] = []
    poker_state: Optional[PlayerStateResponse] = None

    @classmethod
    def from_room(cls, room, request):
        name = request.user.name
        player_id = request.user.uuid
        room_key = request.user.room_key
        game_type = room.table_metadata.game_type

        slots = room.table_metadata.slots
        empty_slots = []
        slot_idx = None
        for i in range(len(slots)):
            if slots[i].player_id == player_id:
                slot_idx = i
            if slots[i].slot_status == SlotStatus.EMPTY:
                empty_slots.append(i)
        if slot_idx == None:
            available_slots = empty_slots

        response = PlayerRetrieveRoomResponse(
            name=name,
            room_key=room_key,
            game_type=game_type,
            slot_idx=slot_idx,
            available_slots=empty_slots,
        )
        get_game_manager(game_type).fill_player_response(response, room, player_id)
        return response


class PlayerSigninRequest(BaseObject):
    room_key: str
    name: str


class PlayerSitRoomRequest(BaseObject):
    slot_idx: int


class PlayerActionRequest(BaseObject):
    poker_action: Optional[PokerAction] = None
