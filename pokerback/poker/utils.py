import random

from pokerback.poker.objects import Card, CardColor, PlayerStatus
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
        colors = [CardColor.SPADE, CardColor.HEART, CardColor.DIAMOND, CardColor.CLUB]
        card_color = colors[int(num / 13)]
        card_num = num % 13 + 1
        cards.append(Card(card_id=num, color=card_color, number=card_num,))
    return cards


def get_next_betting_idx(game, current_idx):
    max_slots = game.table_metadata.max_slots
    slots = game.table_metadata.slots
    next_idx = (current_idx + 1) % max_slots
    while next_idx != current_idx:
        slot = slots[next_idx]
        if slot.slot_status == SlotStatus.ACTIVE:
            player_id = slot.player_id
            if game.player_states[player_id].player_status == PlayerStatus.BETTING:
                return next_idx
        next_idx = (next_idx + 1) % max_slots
    raise Exception("No more players betting")


def get_next_button_idx(room, start_idx):
    max_slots = room.table_metadata.max_slots
    slots = room.table_metadata.slots
    res_idx = start_idx
    while slots[res_idx].slot_status != SlotStatus.ACTIVE:
        res_idx = (res_idx + 1) % max_slots
    return res_idx
