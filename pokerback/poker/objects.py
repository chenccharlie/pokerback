from enum import Enum
from typing import List, Dict

from pokerback.room.objects import TableMetadata
from pokerback.utils.baseobject import BaseObject


class AmountChangeType(Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    NOT_CHANGED = "not_changed"


class AmountChangeLog(BaseObject):
    change_type: AmountChangeType
    amount_changed: int
    game_id: str


class PlayerTokens(BaseObject):
    player_id: str
    amount_available: int
    amount_change_log: List[AmountChangeLog]


class GameMetadata(BaseObject):
    small_blind: int
    button_idx: int = 0


class CardColor(Enum):
    SPADE = "spade"
    HEART = "heart"
    DIAMOND = "diamond"
    CLUB = "club"


class Card(BaseObject):
    card_id: int
    color: CardColor
    number: int


class PlayerStatus(Enum):
    BETTING = "betting"
    FOLDED = "folded"


class PlayerGameState(BaseObject):
    player_id: str
    cards: List[Card]
    amount_betting: int
    amount_available: int
    player_status: PlayerStatus
    pot_won: int


class ActionType(Enum):
    CHECK = "check"
    BET = "bet"
    FOLD = "fold"


class Action(BaseObject):
    player_id: str
    action_type: ActionType
    amount_bet: int


class Pot(BaseObject):
    player_ids: List[str]
    amount: int


class GameStage(Enum):
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOW_HAND = "show_hand"


class GameStatus(Enum):
    PLAYING = "playing"
    OVER = "over"
    PAUSED = "paused"


class Game(BaseObject):
    game_id: str
    table_metadata: TableMetadata
    metadata: GameMetadata
    table_cards: List[Card]
    player_states: Dict[str, PlayerGameState]
    actions: List[Action]
    next_player_id: str
    pots: List[Pot]
    stage: GameStage
    game_status: GameStatus


class PokerGames(BaseObject):
    game_metadata: GameMetadata
    games: List[Game] = []
    players: Dict[str, PlayerTokens] = {}
