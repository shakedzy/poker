from abc import abstractmethod
from utils import *


class Player:
    name = None
    id = None
    chips = None

    hand = list()
    bet = 0

    def __init__(self, name=None):
        self.name = name

    def initialize(self, id, chips):
        self.id = id
        if self.name is None:
            self.name = str(id)
        self.chips = chips

    def deal_card(self, card):
        self.hand.append(card)

    @abstractmethod
    def play(self, board, bets, active_players, possible_actions, history, **kwargs):
        return None

    @abstractmethod
    def receive_reward(self, reward, **kwargs):
        pass

    def __str__(self):
        return 'Player(name={name},id={id},hand={hand},chips={chips},bet={bet})'.format(name=self.name, id=self.id,
                                                                                        hand=cards_to_string(self.hand, no_color=True),
                                                                                        chips=self.chips, bet=self.bet)


class Drunk(Player):
    _dont_fold = False

    def __init__(self, name='Bob', dont_fold=False):
        self._dont_fold = dont_fold
        super(Drunk, self).__init__(name)

    def play(self, board, bets, active_players, possible_actions, history, **kwargs):
        reset_seed()
        actions = list(possible_actions)
        if self._dont_fold and len(actions) > 1:
            actions.remove(Actions.fold)
        action = random.choice(actions)
        return action

    def receive_reward(self, reward, **kwargs):
        pass


class Human(Player):
    def __init__(self, name='User'):
        super(Human, self).__init__(name)

    def play(self, board, bets, active_players, possible_actions, history, **kwargs):
        players_names = kwargs.get('players_names', dict(map(lambda i: (i, str(i)), range(len(bets)))))
        print('* * * * * *')
        print("{n}'s turn (Player ID: {i}):".format(n=self.name, i=self.id))
        print('Board: {}'.format(cards_to_string(board)))
        print('Hand: {}'.format(cards_to_string(self.hand)))
        print('Remaining chips: {}'.format(self.chips))
        print('Bets:')
        for player_id, bet in bets.items():
            print('\t{n} (ID: {i}): {b}'.format(n=players_names[player_id], i=player_id, b=bet))
        print('Possible actions:')
        for a in sorted(possible_actions, key=lambda a: a.value,):
            print('\t{i}: {n}'.format(i=a.value, n=a.name))
        print('Please select an action number:')
        action = int(input())
        while action not in [a.value for a in possible_actions]:
            print('Not a valid action, please try again:')
            action = int(input())
        print('* * * * * *')
        return Actions(action)

    def receive_reward(self, reward, **kwargs):
        pass
