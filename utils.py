import random
import time
from enum import Enum
from treys import Card

Actions = Enum('Actions', 'check match raise_1 raise_2 all_in fold')


def reset_seed():
    random.seed(int(time.time()))


def cards_to_string(cards, no_color=False):
    str_cards = map(lambda c: Card.int_to_pretty_str(c, no_color=no_color), cards)
    return ','.join(str_cards)
