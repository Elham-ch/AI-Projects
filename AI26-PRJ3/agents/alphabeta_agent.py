from agents.search_utils import evaluate, ordered_moves


class AlphaBetaAgent:
    def __init__(self, depth=4, endgame_empty=6):
        self.depth = depth
        self.endgame_empty = endgame_empty
        self.nodes_searched = 0

    def evaluate(self, game, player):
        return evaluate(game, player)

    def choose_move(self, game, player):
        self.nodes_searched = 0
        _, move = self.max_value(
            game, self.depth, player, float("-inf"), float("inf")
        )
        return move

    def max_value(self, game, depth, root_player, alpha, beta):
        self.nodes_searched += 1

        if game.game_over() or (depth <= 0 and not self.should_search_to_end(game)):
            return evaluate(game, root_player), None

        legal_moves = game.get_valid_moves(root_player)
        if not legal_moves:
            opponent_moves = game.get_valid_moves(-root_player)
            if not opponent_moves:
                return evaluate(game, root_player), None
            value, _ = self.min_value(game, depth, root_player, alpha, beta)
            return value, None

        value = float("-inf")
        best_move = None
        for move in ordered_moves(game, legal_moves):
            child = game.copy()
            child.make_move(root_player, *move)
            value2, _ = self.min_value(child, depth - 1, root_player, alpha, beta)
            if value2 > value:
                value = value2
                best_move = move
            alpha = max(alpha, value)
            if value >= beta:
                return value, best_move
        return value, best_move

    def min_value(self, game, depth, root_player, alpha, beta):
        self.nodes_searched += 1

        if game.game_over() or (depth <= 0 and not self.should_search_to_end(game)):
            return evaluate(game, root_player), None

        opponent = -root_player
        legal_moves = game.get_valid_moves(opponent)
        if not legal_moves:
            root_moves = game.get_valid_moves(root_player)
            if not root_moves:
                return evaluate(game, root_player), None
            value, _ = self.max_value(game, depth, root_player, alpha, beta)
            return value, None

        value = float("inf")
        best_move = None
        for move in ordered_moves(game, legal_moves):
            child = game.copy()
            child.make_move(opponent, *move)
            value2, _ = self.max_value(child, depth - 1, root_player, alpha, beta)
            if value2 < value:
                value = value2
                best_move = move
            beta = min(beta, value)
            if value <= alpha:
                return value, best_move
        return value, best_move

    def should_search_to_end(self, game):
        return self.empty_count(game) <= self.endgame_empty

    def empty_count(self, game):
        count = 0
        for row in game.board:
            for cell in row:
                if cell == 0:
                    count += 1
        return count
