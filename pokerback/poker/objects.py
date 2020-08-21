from enum import Enum
from typing import List, Dict, Optional

from pokerback.poker.poker_utils import (
    is_flush,
    is_straight,
    is_straight_flush,
    is_four_of_a_kind,
    is_full_house,
    is_three_of_a_kind,
    is_two_pairs,
    is_pair,
)
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

    @classmethod
    def from_id(cls, num):
        colors = [CardColor.SPADE, CardColor.HEART, CardColor.DIAMOND, CardColor.CLUB]
        card_color = colors[int(num / 13)]
        card_num = num % 13 + 1
        return Card(card_id=num, color=card_color, number=card_num)

    @classmethod
    def from_card(cls, color, number):
        colors = {
            CardColor.SPADE: 0,
            CardColor.HEART: 1,
            CardColor.DIAMOND: 2,
            CardColor.CLUB: 3,
        }
        card_id = colors[color] * 13 + number - 1
        return Card(card_id=card_id, color=color, number=number)

    def sort_key(item):
        return item.number


class HandType(Enum):
    STRAIGHT_FLUSH = "straight_flush"
    FOUR_OF_A_KIND = "four_of_a_kind"
    FULL_HOUSE = "full_house"
    FLUSH = "flush"
    STRAIGHT = "straight"
    THREE_OF_A_KIND = "three_of_a_kind"
    TWO_PAIRS = "two_pairs"
    PAIR = "pair"
    HIGH_CARD = "high_card"


class CardBundle(BaseObject):
    number: int
    cards: List[Card]

    def sort_key(item):
        return (len(item.cards), item.number)


class HandStyle(BaseObject):
    card_bundles: List[CardBundle]

    def counts(self):
        return [len(bundle.cards) for bundle in self.card_bundles]


class Hand(BaseObject):
    hand_type: HandType
    hand_style: HandStyle

    def sorted_cards(self):
        res = []
        for bundle in self.hand_style.card_bundles:
            for card in bundle.cards:
                res.append(card)

        if (
            self.hand_type == HandType.STRAIGHT
            or self.hand_type == HandType.STRAIGHT_FLUSH
        ):
            # Purely sort by increasing number if is straight
            res.sort(key=Card.sort_key)
            if res[0].number == 1 and res[1].number == 10:
                # Move Ace towards the end if is royal straight
                res = res[1:] + res[:1]

        return res

    def __eq__(self, other):
        if self.hand_type != other.hand_type:
            return False
        sorted_cards = self.sorted_cards()
        other_sorted_cards = other.sorted_cards()
        for i in range(5):
            if sorted_cards[i].number != other_sorted_cards[i].number:
                return False
        return True

    def sort_key(item):
        hand_type_grade = {
            HandType.HIGH_CARD: 1,
            HandType.PAIR: 2,
            HandType.TWO_PAIRS: 3,
            HandType.THREE_OF_A_KIND: 4,
            HandType.STRAIGHT: 5,
            HandType.FLUSH: 6,
            HandType.FULL_HOUSE: 7,
            HandType.FOUR_OF_A_KIND: 8,
            HandType.STRAIGHT_FLUSH: 9,
        }
        sorted_cards = item.sorted_cards()
        if (
            item.hand_type == HandType.STRAIGHT
            or item.hand_type == HandType.STRAIGHT_FLUSH
        ):
            return (hand_type_grade[item.hand_type], sorted_cards[1].number, 0, 0, 0, 0)
        else:
            return (
                hand_type_grade[item.hand_type],
                sorted_cards[0].number,
                sorted_cards[1].number,
                sorted_cards[2].number,
                sorted_cards[3].number,
                sorted_cards[4].number,
            )

    @classmethod
    def from_cards(cls, cards):
        assert len(cards) == 5

        hand_style = cls._get_hand_style(cards)
        return cls(
            hand_type=cls._get_hand_type(cards, hand_style), hand_style=hand_style,
        )

    @classmethod
    def _get_hand_style(cls, cards):
        bundles = {}
        for card in cards:
            number = card.number
            if number == 1:
                number = 14
            if number not in bundles:
                bundles[number] = []
            bundles[number].append(card)

        card_bundles = []
        for number in bundles:
            card_bundles.append(CardBundle(number=number, cards=bundles[number]))
        card_bundles.sort(reverse=True, key=CardBundle.sort_key)
        return HandStyle(card_bundles=card_bundles)

    @classmethod
    def _get_hand_type(cls, cards, style):
        if is_straight_flush(cards):
            return HandType.STRAIGHT_FLUSH
        if is_four_of_a_kind(cards, style):
            return HandType.FOUR_OF_A_KIND
        if is_full_house(cards, style):
            return HandType.FULL_HOUSE
        if is_flush(cards):
            return HandType.FLUSH
        if is_straight(cards):
            return HandType.STRAIGHT
        if is_three_of_a_kind(cards, style):
            return HandType.THREE_OF_A_KIND
        if is_two_pairs(cards, style):
            return HandType.TWO_PAIRS
        if is_pair(cards, style):
            return HandType.PAIR
        return HandType.HIGH_CARD


class PlayerHand(BaseObject):
    player_id: str
    best_hand: Hand

    def sort_key(item):
        return Hand.sort_key(item.best_hand)


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
    best_hand: Optional[Hand] = None

    def bet(self, amount):
        assert amount > 0
        assert amount <= self.amount_available
        self.amount_betting += amount
        self.total_betting += amount
        self.amount_available -= amount

    def fold(self):
        self.player_status = PlayerStatus.FOLDED

    def find_best_hand(self, table_cards):
        available_cards = []
        for card in self.cards:
            available_cards.append(card.copy())
        for card in table_cards:
            available_cards.append(card.copy())

        hands = []
        for i in range(6):
            for j in range(i + 1, 7):
                cards = (
                    available_cards[:i]
                    + available_cards[i + 1 : j]
                    + available_cards[j + 1 :]
                )
                assert len(cards) == 5
                hands.append(Hand.from_cards(cards))
        hands.sort(reverse=True, key=Hand.sort_key)
        self.best_hand = hands[0]


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


class Pot(BaseObject):
    pot_amount: int
    winners: List[str]


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
    pots: List[Pot] = []

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
        self.next_player_id = None
        self.game_status = GameStatus.OVER

        # Find all betting players
        betting_players = [
            player_id
            for player_id in self.player_states
            if self.player_states[player_id].player_status == PlayerStatus.BETTING
        ]

        # Find all best hands for betting players
        player_hands = []
        for player_id in betting_players:
            self.player_states[player_id].find_best_hand(self.table_cards)
            player_hands.append(
                PlayerHand(
                    player_id=player_id,
                    best_hand=self.player_states[player_id].best_hand,
                )
            )

        # Rank all the betting players
        player_hands.sort(reverse=True, key=PlayerHand.sort_key)
        player_batches = []
        cur_hand = None
        cur_batch = []
        for player_hand in player_hands:
            if cur_hand is None:
                cur_batch.append(player_hand.player_id)
                cur_hand = player_hand.best_hand
            else:
                if player_hand.best_hand == cur_hand:
                    cur_batch.append(player_hand.player_id)
                else:
                    player_batches.append(cur_batch.copy())
                    cur_batch = [player_hand.player_id]
                    cur_hand = player_hand.best_hand
        if len(cur_batch) > 0:
            player_batches.append(cur_batch.copy())

        player_scores = {}
        for i in range(len(player_batches)):
            player_batch = player_batches[i]
            for player_id in player_batch:
                player_scores[player_id] = len(player_batches) - i

        # Rank betting amount from low to high
        bettings = []
        for player_id in betting_players:
            bet_amount = self.player_states[player_id].total_betting
            bettings.append(
                {"player_id": player_id, "bet_amount": bet_amount,}
            )

        def sort_bet_amount(item):
            return item["bet_amount"]

        bettings.sort(key=sort_bet_amount)

        # Split pot and ssign winning amount to players
        last_bet = 0
        for i in range(len(bettings)):
            cur_bet = bettings[i]["bet_amount"]
            if cur_bet == last_bet:
                # If the same bet amount has been processed, skip
                continue

            # Go over all the players and get their bet amount between last_bet and cur_bet
            pot = 0
            for player_id in self.player_states:
                player_betting = self.player_states[player_id].total_betting
                if player_betting > last_bet:
                    pot += min(player_betting, cur_bet) - last_bet

            # Find out all the winning players for this pot from players betting at least this amount
            winners = []
            cur_score = 0
            for player_id in betting_players:
                player_betting = self.player_states[player_id].total_betting
                if player_betting < cur_bet:
                    continue
                player_score = player_scores[player_id]
                if player_score > cur_score:
                    cur_score = player_score
                    winners = []
                if player_score == cur_score:
                    winners.append(player_id)

            # Split pot to winners to their pot_won
            winning_amount = int(pot / len(winners))
            for player_id in winners:
                self.player_states[player_id].pot_won += winning_amount

            # Record pot split
            self.pots.append(Pot(pot_amount=pot, winners=winners))

            # Replace last_bet with cur_bet
            last_bet = cur_bet

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

        # Record pot
        self.pots.append(Pot(pot_amount=total_pot, winners=[player_left]))

    def should_show_hand(self):
        if not self._are_all_bets_equal():
            # If bets are not equal yet we should not advance to show_hand
            return False

        # We should advance to SHOW_HAND directly if at most 1 betting user has token left
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


class PlayerStateResponse(BaseObject):
    cards: List[Card]
    amount_available: int
    amount_betting: int
    total_betting: int
    pot_won: int
    player_status: PlayerStatus
    game_status: GameStatus
    is_your_turn: bool = False
    min_bet: Optional[int] = None
