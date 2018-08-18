import random
import time
import operator
from treys import Card, Deck, Evaluator


class Game:
    _players_num = None
    _active_players = list()
    _players_bets = dict()
    _players_chips = dict()
    _players_hands = dict()
    _player_to_play = None
    _board = list()
    _dealer = None
    _deck = list()
    _highest_bet = None
    _print_logs = False

    @staticmethod
    def _reset_seed():
        random.seed(int(round(time.time())))

    @staticmethod
    def _cards_to_string(cards):
        str_cards = map(lambda c: Card.int_to_pretty_str(c), cards)
        return ','.join(str_cards)

    def _init_deck(self):
        self._deck = Deck()

    def _set_dealer(self):
        self._reset_seed()
        self._dealer = random.randint(0, self._players_num - 1)
        self._next_player()

    def _next_player(self):
        i = self._active_players.index(self._player_to_play)
        next_i = (i + 1) % (len(self._active_players) - 1)
        self._player_to_play = self._active_players[next_i]

    def _make_bet(self,chips,player=_player_to_play):
        if self._players_chips[player] < chips:
            raise ValueError('Player cannot afford this bet')
        self._players_chips[player] -= chips
        self._players_bets[player] += chips
        if self._players_bets[player] > self._highest_bet:
            self._highest_bet = self._players_bets[player]
        self._next_player()

    def _pass_turn(self,player=_player_to_play):
        if self._players_bets[player] < self._highest_bet:
            raise EnvironmentError('Player caanot pass, must match bet first')
        self._next_player()

    def _fold(self,player=_player_to_play):
        self._active_players.remove(player)
        if len(self._active_players) == 1:
            self._end_game()
        else:
            self._next_player()

    def _deal_players(self):
        for _ in range(2):
            for p in range(self._players_num):
                card = self._deck.draw(1)
                self._players_hands[p].append(card)

    def _rank_hands(self):
        eval = Evaluator()
        ranks = dict()
        for p in self._active_players:
            hand = self._players_hands[p]
            rank = eval.evaluate(hand,self._board)
            ranks[p] = rank
        return ranks

    def _end_game(self):
        if len(self._active_players) == 1:
            winners = self._active_players
        else:
            ranks = self._rank_hands()
            players = sorted(ranks.items(), key=operator.itemgetter(1), reverse=True)
            winners = list()
            best_rank = players[0][1]
            tie = True
            while tie:
                p = players.pop(0)
                if p[1] == best_rank:
                    winners.append(p[0])
                else:
                    tie = False
        prize = sum(map(lambda kv: kv[1], self._players_bets.items()))
        if self._print_logs:
            print('GAME ENDED. Prize: {p}'.format(p=prize))
            print('Dealer: {d}'.format(d=self._dealer))
            print('Board: {b}'.format(b=self._cards_to_string(self._board)))
            for p in range(self._players_num):
                if p in winners:
                    winner_str = 'W'
                else:
                    winner_str = ''
                if p not in self._active_players:
                    folded_str = 'F'
                else:
                    folded_str = ''
                print('Player {p}: {h} Total bet: {b} {w}{f}'.format(p=p,
                                                                     h=self._cards_to_string(self._players_hands[p]),
                                                                     b=self._players_bets[p],
                                                                     w=winner_str,
                                                                     f=folded_str))
            print('--------------------------------------------------')
        return winners, prize

    def __init__(self,players=2,**kwargs):
        if players < 2:
            raise ValueError("Must have at least two players")
        self._print_logs = kwargs.get('print_logs',False)
        self._players_num = players
        self._active_players = list(range(players))
        self._highest_bet = 0
        for p in range(players):
            self._players_bets[p] = 0
            self._players_chips[p] = kwargs.get('chips_per_player',8)
            self._players_hands[p] = list()
        self._set_dealer()
        self._make_bet(1)  # small blind
        self._make_bet(2)  # big blind
        self._init_deck()
        self._deal_players()

    def next_round(self):
        if len(self._board) == 0:
            n = 3
        else:
            n = 1
        for _ in range(n):
            card = self._deck.draw(1)
            self._board.append(card)

    def playing_player(self):
        return self._player_to_play

    def is_round_over(self):
        active_players_bets = [self._players_bets[p] for p in self._active_players]
        return self._player_to_play != self._dealer and active_players_bets[1:] == active_players_bets[:-1]