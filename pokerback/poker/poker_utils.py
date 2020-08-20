def is_flush(cards):
    color = cards[0].color
    for card in cards:
        if card.color != color:
            return False
    return True


def is_straight(cards):
    numbers = [card.number for card in cards]
    numbers.sort()

    if (
        numbers[0] == 1
        and numbers[1] == 10
        and numbers[2] == 11
        and numbers[3] == 12
        and numbers[4] == 13
    ):
        return True
    for i in range(5):
        if numbers[i] - numbers[0] != i:
            return False
    return True


def is_straight_flush(cards):
    return is_straight(cards) and is_flush(cards)


def is_four_of_a_kind(cards, style):
    return style.counts() == [4, 1]


def is_full_house(cards, style):
    return style.counts() == [3, 2]


def is_three_of_a_kind(cards, style):
    return style.counts() == [3, 1, 1]


def is_two_pairs(cards, style):
    return style.counts() == [2, 2, 1]


def is_pair(cards, style):
    return style.counts() == [2, 1, 1, 1]
