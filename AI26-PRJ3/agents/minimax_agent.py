# TODO: STUDENT IMPLEMENTATION

class MinimaxAgent:
    def __init__(self, depth=4):
        self.depth = depth

    def evaluate(self, game, player):
        raise NotImplementedError

    def minimax(self, game, depth, maximizing, root_player):
        raise NotImplementedError

    def choose_move(self, game, player):
        value, move = self.minimax(game, self.depth, True, player)
        return move
