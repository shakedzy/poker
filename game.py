import operator
from treys import Deck, Evaluator
from utils import *


class Game:
    players = list()
    active_players = list()
    players_names = dict()
    playing_player = None
    board = list()
    dealer = None
    highest_bet = 0
    game_over = False
    jackpot = 0
    history = list()

    _deck = list()
    _print_logs = True
    _all_in_players = set()

    def _init_deck(self):
        self._deck = Deck()

    def _set_dealer(self):
        reset_seed()
        self.dealer = random.randint(0, len(self.players) - 1)
        self.playing_player = self.dealer

    def _next_player(self):
        i = self.active_players.index(self.playing_player)
        next_i = (i + 1) % len(self.active_players)
        self.playing_player = self.active_players[next_i]

    def _make_bet(self, chips, player):
        if self._print_logs:
            print('Player {p} adds {c} chips to the bet'.format(p=player, c=chips))
        if self.players[player].chips < chips:
            raise PokerException('Player cannot afford this bet')
        self.players[player].chips -= chips
        self.players[player].bet += chips
        self.jackpot += chips
        if self.players[player].bet > self.highest_bet:
            self.highest_bet = self.players[player].bet

    def _pass_turn(self, player):
        if self.players[player].bet < self.highest_bet:
            raise PokerException('Player cannot check, must match bet first')

    def _fold(self, player):
        winners = list()
        self.active_players.remove(player)
        if len(self.active_players) == 1:
            winners = self._end_game()
        return winners

    def _deal_players(self):
        for _ in range(2):
            for p in range(len(self.players)):
                card = self._deck.draw(1)
                self.players[p].deal_card(card)

    def _rank_hands(self):
        ev = Evaluator()
        ranks = dict()
        for p in self.active_players:
            hand = self.players[p].hand
            rank = ev.evaluate(hand, self.board)
            ranks[p] = rank
        return ranks

    def _end_game(self):
        self.game_over = True
        if len(self.active_players) == 1:
            winners = self.active_players
        else:
            ranks = self._rank_hands()
            players = sorted(ranks.items(), key=operator.itemgetter(1))
            winners = list()
            best_rank = players[0][1]
            tie = True
            while tie and len(players) > 0:
                p = players.pop(0)
                if p[1] == best_rank:
                    winners.append(p[0])
                else:
                    tie = False
        if self._print_logs:
            print('--------------------------------------------------')
            print('GAME ENDED. Jackpot: {j}'.format(j=self.jackpot))
            print('Dealer: {d}'.format(d=self.dealer))
            print('Board: {b}'.format(b=cards_to_string(self.board)))
            for p in range(len(self.players)):
                if p in winners:
                    winner_str = 'W'
                else:
                    winner_str = ''
                if p not in self.active_players:
                    folded_str = 'F'
                else:
                    folded_str = ''
                if self.players[p].name is None:
                    player_name = str(p)
                else:
                    player_name = '{0} ({1})'.format(self.players[p].name, p)
                print('Player {p}: {h} Total bet: {b} {w}{f}'.format(p=player_name,
                                                                     h=cards_to_string(self.players[p].hand),
                                                                     b=self.players[p].bet,
                                                                     w=winner_str,
                                                                     f=folded_str))
            print('--------------------------------------------------')
        return winners

    def _next_round(self):
        winners = list()
        if len(self.board) == 5:
            winners = self._end_game()
        else:
            if len(self.board) == 0:
                n = 3
            else:
                n = 1
            for _ in range(n):
                card = self._deck.draw(1)
                self.board.append(card)
            if n > 1:
                crd = 'cards'
            else:
                crd = 'card'
            if self._print_logs:
                print(' --> Drawing {0} {1}'.format(n, crd))
                print('Board: {}'.format(cards_to_string(self.board)))
        return winners

    def _play_round(self):
        winners = list()
        round_start = True
        while round_start or (not winners and not self._is_round_over()):
            round_start = False
            if self.playing_player in self._all_in_players:
                if self._print_logs:
                    print('Player {} is all in'.format(self.playing_player))
                self._next_player()
            else:
                bets = dict(map(lambda p: (p[0], p[1].bet), enumerate(self.players)))
                valid_action = False
                while not valid_action:
                    try:
                        action = self.players[self.playing_player].play(self.board, bets, self.active_players,
                                                                        self._get_possible_actions(self.playing_player),
                                                                        self.history, players_names=self.players_names)
                        if self._print_logs:
                            print('Player {p} chose to {a}'.format(p=self.playing_player, a=action.name))
                        if action == Actions.check:
                            self._pass_turn(self.playing_player)
                        elif action in [Actions.match, Actions.raise_1, Actions.raise_2]:
                            bet = self.highest_bet - self.players[self.playing_player].bet
                            if action == Actions.raise_1:
                                bet += 1
                            elif action == Actions.raise_2:
                                bet += 2
                            self._make_bet(bet, self.playing_player)
                        elif action == Actions.all_in:
                            self._make_bet(self.players[self.playing_player].chips, self.playing_player)
                            self._all_in_players.add(self.playing_player)
                        else:
                            winners = self._fold(self.playing_player)
                        if not winners:
                            self._next_player()
                        valid_action = True
                        self.history.append(action)
                    except PokerException:
                        print('This action is forbidden, select another action')
        return winners

    def _is_round_over(self):
        active_players_bets = [self.players[p].bet for p in self.active_players]
        return self.playing_player != self.dealer and active_players_bets[1:] == active_players_bets[:-1]

    def _get_possible_actions(self, player):
        actions = set()
        min_bet = self.highest_bet - self.players[player].bet
        chips = self.players[player].chips
        if chips < min_bet:
            pass
        elif chips == 0:
            actions.add(Actions.check)
        else:  # chips >= min_bet
            actions.add(Actions.all_in)
            if min_bet == 0:
                actions.add(Actions.check)
            elif min_bet < chips:
                actions.add(Actions.match)
            if chips - min_bet > 1:
                actions.add(Actions.raise_1)
            if chips - min_bet > 2:
                actions.add(Actions.raise_2)
        actions.add(Actions.fold)
        return actions

    def __init__(self, players, chips_per_player=10, print_info=True):
        if len(players) < 2:
            raise ValueError("Must have at least two players")
        self._print_logs = print_info
        self.players = players
        for i, p in enumerate(self.players):
            p.initialize(id=i, chips=chips_per_player)
            self.players_names[i] = p.name
        self.active_players = list(range(len(players)))
        self.highest_bet = 0
        self.jackpot = 0
        self.game_over = False
        for p in range(len(players)):
            self.players[p].bet = 0
            self.players[p].chips = chips_per_player
            self.players[p].hand = list()
        self._set_dealer()
        self._next_player()
        self._make_bet(1, self.playing_player)  # small blind
        self._next_player()
        self._make_bet(2, self.playing_player)  # big blind
        self._next_player()
        self._init_deck()
        self._deal_players()

    def start(self):
        if self._print_logs:
            print('Starting game...')
            print('Dealer: {}'.format(self.dealer))
        winners = list()
        while not winners:
            winners = self._play_round()
            if not winners:
                winners = self._next_round()
        for p in self.players:
            if p.id in winners:
                r = float(self.jackpot) / len(winners)
            else:
                r = 0.0
            r -= p.bet
            if self._print_logs:
                print('Player {0} reward: {1}'.format(p.id, r))
            p.receive_reward(r)

    def __str__(self):
        return 'Game(players={players},'.format(players=[str(p) for p in self.players]) + \
               'active_players={ap},playing_player={pp},'.format(ap=self.active_players, pp=self.playing_player) + \
               'dealer={dealer},board={board},highest_bet={hb},jackpot={jp},game_over={go})'.format(dealer=self.dealer,
                                                                                                     board=cards_to_string(self.board, no_color=True),
                                                                                                     hb=self.highest_bet,
                                                                                                     jp=self.jackpot,
                                                                                                     go=self.game_over)
