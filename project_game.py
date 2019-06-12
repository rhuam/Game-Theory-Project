import random
import numpy as np

class Player:

    def __init__(self, id):
        self.id = id
        self.card = None

        self.state_value = None
        self.action_value = None

        self.qtable = np.matrix(np.zeros([117, 2]))

        self._fold = False
        self._bet = False
        self._reward = 0


    @property
    def action(self):
        if self._fold:
            return "fold"
        elif self._bet:
            return "bet"
        else:
            return "unknown"

    @property
    def reward(self):
        return self._reward

    def set_reward(self, value):
        self._reward = value

    def restart(self):
        self._fold = False
        self._bet = False

    def fold(self):
        self._fold = True

    def bet(self):
        self._bet = True

    def epsilon_greedy(self, state, train=False):

        if train or np.random.rand() < 0.9:
            action = np.argmax(self.qtable[state, :])
        else:
            action = np.random.randint(0, 2)

        if action == 0:
            self.fold()
        elif action == 1:
            self.bet()
        return action


    def chose(self, players):
        pl = players.copy()
        pl.remove(self)
        state = 0

        state_list = list()

        for p in pl:
            if p.action == 'fold':
                state_list.append(0)
            elif p.action == 'bet':
                state_list.append(1)
            elif p.action == 'unknown':
                state_list.append(2)

        state_list.append(self.card.value - 1)

        n = 39
        for s in state_list[:-1]:
            state += s*n
            n /= 3
        state += state_list[-1]

        print(state)
        self.state_value = int(state)
        self.action_value = self.epsilon_greedy(self.state_value)


    def ql(self, alpha):
        self.qtable[self.state_value, self.action_value] += alpha * (self._reward - self.qtable[self.state_value, self.action_value])

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


        for p in self.players:
            if p.action == "fold":
                playeres_fold.append(p)
            elif p.action == "bet":
                playeres_bet.append(p)


        for p in playeres_fold:
            p.set_reward(0)

        if len(playeres_bet) >= 1:
            maior = playeres_bet[0]

            for p in playeres_bet:
                p.set_reward(-5)
                if p.card.value > maior.card.value:
                    maior = p

            maior.set_reward(10)


        for player in self.players:
            print("%s: action (%s) reward(%s) card(%s)"% (player, player.action, player.reward, player.card))



    def round(self):
        self.deck = Deck()
        self.deck.shuffle()
        for player in self.players:
            player.restart()
            player.card = self.deck.deal_the_cards()



        for player in self.players:
            player.chose(self.players)

        self.reward()

        for player in self.players:
            player.ql(0.8)


if __name__ == "__main__":
    t = Table(3)

    for i in range(10000):
        print("Step", i)
        t.round()


    for p in t.players:
        i = 0
        print(p, "--- QTABLE")
        for q in p.qtable:
            print(i%13 + 1, q[:, 1], sep='\t')
            i += 1
        print("\n\n")

