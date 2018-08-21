import random
import time
from enum import Enum
from treys import Card

Actions = Enum('Actions', 'check match raise_1 raise_2 all_in fold')


class PokerException(Exception):
    def __init__(self, *args, **kwargs):
        pass


def reset_seed():
    random.seed(int(time.time()))


def cards_to_string(cards, no_color=False):
    if no_color:
        str_func = Card.int_to_str
    else:
        str_func = Card.int_to_pretty_str
    str_cards = map(lambda c: str_func(c), cards)
    return ','.join(str_cards)
