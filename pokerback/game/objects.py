from enum import Enum
from typing import NamedTuple, List, Dict, Optional


class SlotStatus(Enum):
    ACTIVE = 1
    SPECTATE = 2
    EMPTY = 3


class Slot(NamedTuple):
    player_id: Optional[str]
    slot_status: SlotStatus


class GameMetadata(NamedTuple):
    max_slots: int
    slots: List[Slot]
    button_idx: int
    small_blind: int
    action_seconds_limit: int


class CardColor(Enum):
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    CLUB = 4


class Card(NamedTuple):
    card_id: int
    color: CardColor
    number: int


class PlayerStatus(Enum):
    BETTING = 1
    FOLDED = 2


class PlayerGameState(NamedTuple):
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


class Action(NamedTuple):
    player_id: str
    action_type: ActionType
    amount_bet: int


class Pot(NamedTuple):
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


class Game(NamedTuple):
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


class AmountChangeLog(NamedTuple):
    change_type: AmountChangeType
    amount_changed: int
    game_id: str


class Player(NamedTuple):
    player_id: str
    amount_available: int
    amount_change_log: List[AmountChangeLog]


class Room(NamedTuple):
    room_key: str
    host_user_id: str
    game_metadata: GameMetadata
    games: List[Game]
    players: Dict[str, Player]