#%%
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from records import matches, ratings

from scipy.interpolate import make_interp_spline, BSpline

ratings = {"Trung": 1500, "Michael": 1500, "Asier": 1500, "Christian": 1500}

# Theory: https://towardsdatascience.com/developing-a-generalized-elo-rating-system-for-multiplayer-games-b9b495e87802

DIFF = 700
K = 50
ALPHA = 4


class History:
    def __init__(self, init_ratings) -> None:
        self._ratings = init_ratings
        self.history = defaultdict(list)
        self.update_history()

    def update_history(self):
        for k, v in self._ratings.items():
            self.history[k].append(v)

    @property
    def ratings(self):
        return self._ratings

    @ratings.setter
    def ratings(self, ratings):
        self._ratings = self.reset_ratings(ratings)
        self.update_history()

    def reset_ratings(self, ratings):
        return {k: max(1400, v) for k, v in ratings.items()}

    def __repr__(self) -> str:
        return str(self._ratings)


def winning_probability(ratings: dict, diff: int = DIFF):
    """
    Calculate probablity of winning for each player.

    Parameters
    ----------
    ratings:
        Rating of each player
    diff:
        Player A has 90% chance of winning if R_A = R_B + DIFF.
        In other words, how easy it is for weaker player to breach the gap
    """
    rv = {}
    N = len(ratings)
    for player1, rating1 in ratings.items():
        num = 0
        for player2, rating2 in ratings.items():
            if player1 == player2:
                continue
            num += 1 / (1 + 10 ** ((rating2 - rating1) / diff))
        den = N * (N - 1) / 2
        rv[player1] = num / den
    return rv


def final_scores(pos, no_pos=2, alpha=ALPHA):
    """
    Calculate final score based on winning position.

    Parameters
    ----------
    pos:
        Final position, 1 is winner, 2 is 2nd winner, ... N is loser
    no_players:
        Number of positions in the game
    alpha:
        How many points 1st winner gets compared to 2nd and 3rd.
        Only matters in games with > 2 final position
    """
    if no_pos == 1:
        return 0.5
    num = alpha ** (no_pos - pos) - 1
    den = sum(alpha ** (no_pos - i) - 1 for i in range(1, no_pos + 1))
    return num / den


def calculate_new_ratings(ratings, match, award=K):
    """
    Calculate new ratings for each player

    Parameters
    ----------
    all_ratings:
        Rating of all players
    match:
        Match result.
        [[A], [B, C], [D]] means A ranks 1st, B & C both rank 2nd, D ranks last
    award: how much does winner get awarded
    """
    players = []
    player_scores = {}
    player_ratings = {}
    for pos, names in enumerate(match, 1):
        for name in names:
            players.append(name)
            player_scores[name] = final_scores(pos, len(match))
            player_ratings[name] = ratings[name]

    win_chance = winning_probability(player_ratings)
    for name in players:
        ratings[name] += (
            award * (len(players) - 1) * (player_scores[name] - win_chance[name])
        )
    return ratings


def plot_hist(history):
    _, ax = plt.subplots(figsize=(10, 7))
    for person, scores in history.history.items():
        plt.plot(scores, label=person, marker="o")
        x, y = len(scores) - 1, scores[-1] + 0.2
        ax.annotate(round(scores[-1]), (x, y))
    plt.legend(loc="upper left")
    plt.ylabel("Rating")
    plt.xlabel("Play")
    plt.show()


def main():
    history = History(ratings)
    for match in matches:
        history.ratings = calculate_new_ratings(ratings, match)
    plot_hist(history)


if __name__ == "__main__":
    main()

# %%