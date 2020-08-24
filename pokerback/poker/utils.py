import random

from pokerback.poker.objects import Card, PlayerStatus, AmountChangeLog
from pokerback.room.objects import SlotStatus


def get_random_cards(num_cards):
    res = []
    while len(res) < num_cards:
        new_card = random.randint(0, 51)
        while new_card in set(res):
            new_card = random.randint(0, 51)
        res.append(new_card)

    cards = []
    for num in res:
        cards.append(Card.from_id(num))
    return cards


def get_next_button_idx(room, start_idx):
    max_slots = room.table_metadata.max_slots
    slots = room.table_metadata.slots
    res_idx = start_idx % max_slots
    while slots[res_idx].slot_status != SlotStatus.ACTIVE:
        res_idx = (res_idx + 1) % max_slots
    return res_idx


def get_player_min_bet(player_states, player_id):
    # Find the max bet on the table
    max_bet = 0
    for p_id in player_states:
        max_bet = max(max_bet, player_states[p_id].total_betting)
    return min(
        player_states[player_id].amount_available,
        max_bet - player_states[player_id].total_betting,
    )


def handle_game_over_player_update(players, game):
    # Apply player token change
    for player_id in game.player_states:
        player_state = game.player_states[player_id]
        amount_changed = player_state.pot_won - player_state.total_betting

        players[player_id].amount_available += amount_changed
        players[player_id].amount_change_log.append(
            AmountChangeLog(amount_changed=amount_changed, game_id=game.game_id,)
        )
