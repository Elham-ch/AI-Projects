class GreedyAgent:
    def choose_move(self, game, player):
        moves = game.get_valid_moves(player)
        if not moves:
            return None
        best = None
        best_score = -10 ** 9
        for move in moves:
            g = game.copy()
            before = sum(cell == player for row in g.board for cell in row)
            g.make_move(player, *move)
            after = sum(cell == player for row in g.board for cell in row)
            gain = after - before
            if gain > best_score:
                best_score = gain
                best = move
        return best
