import random


class RandomAgent:
    def choose_move(self, game, player):
        moves = game.get_valid_moves(player)
        return random.choice(moves) if moves else None
