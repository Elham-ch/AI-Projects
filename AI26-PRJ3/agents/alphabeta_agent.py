# TODO: STUDENT IMPLEMENTATION

class AlphaBetaAgent:
    def __init__(self, depth=4):
        self.depth = depth

    def evaluate(self, game, player):
        raise NotImplementedError

    def alphabeta(self, game, depth, alpha, beta, maximizing, root_player):
        raise NotImplementedError

    def choose_move(self, game, player):
        value, move = self.alphabeta(
            game, self.depth, float('-inf'), float('inf'), True, player
        )
        return move
