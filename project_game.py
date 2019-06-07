import random
import numpy as np

class Player:

    def __init__(self, id):
        self.id = id

        self.card = None

        self._fold = False
        self._check = False
        self._bet = False

        self._reward = 0

        self.qtable = np.matrix(np.zeros([208,3]))

    @property
    def action(self):
        return "fold" if self._fold else "check" if self._check else "bet" if self._bet else "unknown"

    @property
    def reward(self):
        return self._reward

    def set_reward(self, value):
        self._reward = value

    def fold(self):
        self._fold = True

    def check(self):
        self._check = True

    def bet(self):
        self._bet = True

    def epsilon_greedy(self, Q, epsilon, n_actions, s, train=False):

        if train or np.random.rand() < epsilon:
            action = np.argmax(Q[s, :])
        else:
            action = np.random.randint(0, n_actions)

        if action == 0:
            self.fold()
        elif action == 1:
            self.check()
        else:
            self.bet()
        return action

    def ql(self, players):
        alpha = 0.8

        pl = players.copy()

        pl.remove(self)

        state = 0

        n = 52
        for p in players:
            n = int(n/4)
            if p.action == 'fold':
                state += 0 * n
            elif p.action == 'check':
                state += 1 * n
            elif p.action == 'bet':
                state += 2 * n
            elif p.action == 'unknown':
                state += 3 * n

        state += (self.card.value - 1)


        # print("state", state)
        # print("card", self.card.value)
        # print("reward", self.reward)

        print(self.qtable)
        action = self.epsilon_greedy(self.qtable, 0.2, 3, 207)
        self.qtable[state, action] += alpha * ( self._reward - self.qtable[state, action])

    def __repr__(self):
        return "Player %s" % (str(self.id))

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return "%s of %s" % (str(self.value), str(self.suit))

class Deck:
    def __init__(self):
        self.cards = list()
        for s in ['clubs', 'diamonds', 'hearts', 'spades']:
            for v in range(1, 14):
                self.cards.append(Card(s, v))

    def deal_the_cards(self):
        return self.cards.pop()

    def shuffle(self):
        random.shuffle(self.cards)

class Table:
    def __init__(self, n_players):
        self.players = [Player(i) for i in range(n_players)]

    def reward(self):

        playeres_fold = list()
        playeres_bet= list()
        playeres_check = list()

        for p in self.players:
            if p.action == "fold":
                playeres_fold.append(p)
            elif p.action == "bet":
                playeres_bet.append(p)
            elif p.action == "check":
                playeres_check.append(p)

        for p in playeres_fold:
            p.set_reward(0)

        if len(playeres_bet) >= 1:
            maior = playeres_bet[0]

            for p in playeres_bet:
                p.set_reward(-5)
                if p.card.value > maior.card.value:
                    maior = p

            maior.set_reward(10)

            for p in playeres_check:
                p.set_reward(-10)

        elif len(playeres_check) >= 1:
            maior = playeres_check[0]

            for p in playeres_check:
                p.set_reward(-10)
                if p.card.value > maior.card.value:
                    maior = p

            maior.set_reward(5)

        for player in self.players:
            print(player, player.action, player.reward)


    def round(self):
        self.deck = Deck()
        self.deck.shuffle()
        for player in self.players:
            player.card = self.deck.deal_the_cards()

        for player in self.players:
            player.ql(self.players)
        self.reward()



if __name__ == "__main__":
    t = Table(3)

    for i in range(100):
        print(">", i)
        t.round()
