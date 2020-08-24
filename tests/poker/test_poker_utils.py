import pytest

from pokerback.poker.objects import Card, CardColor
from pokerback.poker.poker_utils import Hand, HandType


@pytest.mark.django_db
def test_form_hand():
    cards = [
        Card.from_card(color=CardColor.SPADE, number=8),
        Card.from_card(color=CardColor.SPADE, number=5),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.HEART, number=2),
        Card.from_card(color=CardColor.SPADE, number=4),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.HIGH_CARD

    cards = [
        Card.from_card(color=CardColor.SPADE, number=2),
        Card.from_card(color=CardColor.CLUB, number=2),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.CLUB, number=9),
        Card.from_card(color=CardColor.SPADE, number=4),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.PAIR

    cards = [
        Card.from_card(color=CardColor.SPADE, number=8),
        Card.from_card(color=CardColor.CLUB, number=4),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.HEART, number=1),
        Card.from_card(color=CardColor.SPADE, number=4),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.TWO_PAIRS

    cards = [
        Card.from_card(color=CardColor.SPADE, number=8),
        Card.from_card(color=CardColor.CLUB, number=4),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.HEART, number=4),
        Card.from_card(color=CardColor.SPADE, number=4),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.THREE_OF_A_KIND

    cards = [
        Card.from_card(color=CardColor.SPADE, number=8),
        Card.from_card(color=CardColor.CLUB, number=4),
        Card.from_card(color=CardColor.SPADE, number=6),
        Card.from_card(color=CardColor.HEART, number=5),
        Card.from_card(color=CardColor.SPADE, number=7),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.STRAIGHT

    cards = [
        Card.from_card(color=CardColor.SPADE, number=3),
        Card.from_card(color=CardColor.CLUB, number=4),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.HEART, number=5),
        Card.from_card(color=CardColor.SPADE, number=2),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.STRAIGHT

    cards = [
        Card.from_card(color=CardColor.SPADE, number=13),
        Card.from_card(color=CardColor.CLUB, number=12),
        Card.from_card(color=CardColor.SPADE, number=10),
        Card.from_card(color=CardColor.HEART, number=11),
        Card.from_card(color=CardColor.SPADE, number=1),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.STRAIGHT

    cards = [
        Card.from_card(color=CardColor.SPADE, number=8),
        Card.from_card(color=CardColor.SPADE, number=5),
        Card.from_card(color=CardColor.SPADE, number=3),
        Card.from_card(color=CardColor.SPADE, number=1),
        Card.from_card(color=CardColor.SPADE, number=4),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.FLUSH

    cards = [
        Card.from_card(color=CardColor.SPADE, number=4),
        Card.from_card(color=CardColor.CLUB, number=12),
        Card.from_card(color=CardColor.DIAMOND, number=4),
        Card.from_card(color=CardColor.HEART, number=4),
        Card.from_card(color=CardColor.SPADE, number=12),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.FULL_HOUSE

    cards = [
        Card.from_card(color=CardColor.SPADE, number=4),
        Card.from_card(color=CardColor.CLUB, number=4),
        Card.from_card(color=CardColor.DIAMOND, number=4),
        Card.from_card(color=CardColor.HEART, number=4),
        Card.from_card(color=CardColor.SPADE, number=12),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.FOUR_OF_A_KIND

    cards = [
        Card.from_card(color=CardColor.DIAMOND, number=4),
        Card.from_card(color=CardColor.DIAMOND, number=2),
        Card.from_card(color=CardColor.DIAMOND, number=6),
        Card.from_card(color=CardColor.DIAMOND, number=5),
        Card.from_card(color=CardColor.DIAMOND, number=3),
    ]
    hand = Hand.from_cards(cards)
    assert hand.hand_type == HandType.STRAIGHT_FLUSH
