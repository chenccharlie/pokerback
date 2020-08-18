from typing import List, Dict, Optional

from pokerback.room.objects import TableMetadata
from pokerback.utils.baseobject import BaseObject
from pokerback.utils.enums import ModelEnum


class AmountChangeType(ModelEnum):
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
    amount_change_log: List[AmountChangeLog] = []


class GameMetadata(BaseObject):
    small_blind: int
    init_token: int
    button_idx: int = -1


class CardColor(ModelEnum):
    SPADE = "spade"
    HEART = "heart"
    DIAMOND = "diamond"
    CLUB = "club"


class Card(BaseObject):
    card_id: int
    color: CardColor
    number: int


class PlayerStatus(ModelEnum):
    BETTING = "betting"
    FOLDED = "folded"


class PlayerGameState(BaseObject):
    player_id: str
    cards: List[Card]
    amount_available: int
    amount_betting: int = 0
    player_status: PlayerStatus = PlayerStatus.BETTING
    pot_won: int = 0


class ActionType(ModelEnum):
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


class GameStage(ModelEnum):
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOW_HAND = "show_hand"


class GameStatus(ModelEnum):
    PLAYING = "playing"
    OVER = "over"
    PAUSED = "paused"


class Game(BaseObject):
    game_id: int
    table_metadata: TableMetadata
    game_metadata: GameMetadata
    table_cards: List[Card]
    player_states: Dict[str, PlayerGameState] = {}
    next_player_id: Optional[str] = None
    actions: List[Action] = []
    pots: List[Pot] = []
    stage: GameStage = GameStage.PRE_FLOP
    game_status: GameStatus = GameStatus.PLAYING


class PokerGames(BaseObject):
    game_metadata: GameMetadata
    games: List[Game] = []
    players: Dict[str, PlayerTokens] = {}
