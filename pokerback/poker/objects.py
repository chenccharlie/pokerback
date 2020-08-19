from typing import List, Dict, Optional

from pokerback.room.objects import TableMetadata, SlotStatus
from pokerback.utils.baseobject import BaseObject
from pokerback.utils.enums import ModelEnum


class AmountChangeLog(BaseObject):
    amount_changed: int
    game_id: int


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
    total_betting: int = 0
    player_status: PlayerStatus = PlayerStatus.BETTING
    pot_won: int = 0

    def bet(self, amount):
        assert amount > 0
        assert amount <= self.amount_available
        self.amount_betting += amount
        self.total_betting += amount
        self.amount_available -= amount

    def fold(self):
        self.player_status = PlayerStatus.FOLDED


class GameStage(ModelEnum):
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOW_HAND = "show_hand"

    @classmethod
    def get_next(cls, stage):
        next_map = {
            cls.PRE_FLOP: cls.FLOP,
            cls.FLOP: cls.TURN,
            cls.TURN: cls.RIVER,
            cls.RIVER: cls.SHOW_HAND,
        }
        return next_map[stage]


class ActionType(ModelEnum):
    CHECK = "check"
    BET = "bet"
    FOLD = "fold"


class Action(BaseObject):
    player_id: str
    game_stage: GameStage
    action_type: ActionType
    amount_bet: int = 0


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
    stage: GameStage = GameStage.PRE_FLOP
    game_status: GameStatus = GameStatus.PLAYING

    def get_player_idx(self, player_id):
        for idx in range(self.table_metadata.max_slots):
            slot = self.table_metadata.slots[idx]
            if slot.slot_status == SlotStatus.ACTIVE and slot.player_id == player_id:
                return idx
        raise Exception("Player not found")

    def get_next_betting_idx(self, current_idx):
        max_slots = self.table_metadata.max_slots
        slots = self.table_metadata.slots
        next_idx = (current_idx + 1) % max_slots
        while next_idx != current_idx:
            slot = slots[next_idx]
            if slot.slot_status == SlotStatus.ACTIVE:
                player_id = slot.player_id
                if self.player_states[player_id].player_status == PlayerStatus.BETTING:
                    return next_idx
            next_idx = (next_idx + 1) % max_slots
        raise Exception("No more players betting")

    def _are_all_bets_equal(self):
        # Find the max bet on the table
        max_bet = 0
        for player_id in self.player_states:
            max_bet = max(max_bet, self.player_states[player_id].total_betting)
        # Find if all bets are equal or to their best available
        for player_id in self.player_states:
            if (
                self.player_states[player_id].total_betting < max_bet
                and self.player_states[player_id].amount_available > 0
            ):
                return False
        return True

    def is_stage_complete(self):
        # Determine whether a stage is complete by looking at whether all active players have at least one action, AND all betting users bet either the largest bet, or all available tokens.
        active_players = self.table_metadata.get_active_players()

        # Find all the players that have had an action in this stage
        acked_players = set(
            [
                action.player_id
                for action in self.actions
                if action.game_stage == self.stage
            ]
        )
        if len(active_players.difference(acked_players)) > 0:
            # Existing active player not acked yet
            return False

        # Return whether all bets are equal
        return self._are_all_bets_equal()

    def advance_stage(self, next_stage=None):
        # Clear the bettings on current stage from player states
        for player_id in self.player_states:
            self.player_states[player_id].amount_betting = 0

        # Advance stage
        self.stage = next_stage or GameStage.get_next(self.stage)

        if self.stage == GameStage.SHOW_HAND:
            # If game is at SHOW_HAND, handle SHOW_HAND and end game
            self.handle_show_hand()
        else:
            # If not, reset next_player to small blind idx
            self.next_player_id = self.table_metadata.slots[
                self.get_next_betting_idx(self.game_metadata.button_idx)
            ].player_id

    def handle_show_hand(self):
        # TODO

        self.next_player_id = None
        self.game_status = GameStatus.OVER

        # Rank all the betting players

        # Calculate total pot

        # Assign winning amount to players

    def is_folding(self):
        # Check if only 1 player is betting
        betting_players = [
            player_id
            for player_id in self.player_states
            if self.player_states[player_id].player_status == PlayerStatus.BETTING
        ]
        return len(betting_players) == 1

    def handle_fold(self):
        self.next_player_id = None
        self.game_status = GameStatus.OVER

        # Calculate total pot
        total_pot = 0
        player_left = None
        for player_id in self.player_states:
            total_pot += self.player_states[player_id].total_betting
            if self.player_states[player_id].player_status == PlayerStatus.BETTING:
                player_left = player_id

        # Assign all pot to the only player left
        self.player_states[player_left].pot_won = total_pot

    def should_show_hand(self):
        if not self._are_all_bets_equal():
            # If bets are not equal yet we should not advance to show_hand
            return False

        # We should advance to SHOW_HAND directly if at most 1 betting user has token left, and the one left is betting the most
        capable_players = [
            player_id
            for player_id in self.player_states
            if self.player_states[player_id].player_status == PlayerStatus.BETTING
            and self.player_states[player_id].amount_available > 0
        ]
        return len(capable_players) <= 1


class PokerGames(BaseObject):
    game_metadata: GameMetadata
    games: List[Game] = []
    players: Dict[str, PlayerTokens] = {}
