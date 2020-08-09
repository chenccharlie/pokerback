import random
import uuid
from enum import Enum
from typing import List, Dict, Optional

from pokerback.utils.baseobject import BaseObject, BaseRedisObject


class SlotStatus(Enum):
    ACTIVE = 1
    SPECTATE = 2
    EMPTY = 3


class Slot(BaseObject):
    player_id: Optional[str] = None
    slot_status: SlotStatus = SlotStatus.EMPTY


class GameMetadata(BaseObject):
    max_slots: int
    slots: List[Slot]
    small_blind: int
    action_seconds_limit: int
    button_idx: int = 0


class CardColor(Enum):
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    CLUB = 4


class Card(BaseObject):
    card_id: int
    color: CardColor
    number: int


class PlayerStatus(Enum):
    BETTING = 1
    FOLDED = 2


class PlayerGameState(BaseObject):
    player_id: str
    cards: List[Card]
    amount_betting: int
    amount_available: int
    player_status: PlayerStatus
    pot_won: int


class ActionType(Enum):
    CHECK = 1
    BET = 2
    FOLD = 3


class Action(BaseObject):
    player_id: str
    action_type: ActionType
    amount_bet: int


class Pot(BaseObject):
    player_ids: List[str]
    amount: int


class GameStage(Enum):
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOW_HAND = 5


class GameStatus(Enum):
    PLAYING = 1
    OVER = 2
    PAUSED = 3


class Game(BaseObject):
    game_id: str
    metadata: GameMetadata
    table_cards: List[Card]
    player_states: Dict[str, PlayerGameState]
    actions: List[Action]
    next_player_id: str
    pots: List[Pot]
    stage: GameStage
    game_status: GameStatus


class AmountChangeType(Enum):
    INCREASE = 1
    DECREASE = 2
    NOT_CHANGED = 3


class AmountChangeLog(BaseObject):
    change_type: AmountChangeType
    amount_changed: int
    game_id: str


class Player(BaseObject):
    player_id: str
    amount_available: int
    amount_change_log: List[AmountChangeLog]


class Room(BaseRedisObject):
    room_uuid: str
    room_key: str
    host_user_id: str
    game_metadata: GameMetadata
    games: List[Game] = []
    players: Dict[str, Player] = {}

    object_key_prefix = "room_"

    def get_object_key(self):
        return self.room_uuid

    @classmethod
    def create_room(
        cls, host_user_id, max_slots=8, small_blind=10, action_seconds_limit=30
    ):
        room_uuid = str(uuid.uuid4())
        room_key = "".join([chr(ord("A") + random.randint(0, 25)) for x in range(5)])

        room = Room(
            room_uuid=room_uuid,
            room_key=room_key,
            host_user_id=host_user_id,
            game_metadata=GameMetadata(
                max_slots=max_slots,
                small_blind=small_blind,
                action_seconds_limit=action_seconds_limit,
                slots=[Slot() for x in range(max_slots)],
            ),
        )
        room.save()
        return room_uuid
