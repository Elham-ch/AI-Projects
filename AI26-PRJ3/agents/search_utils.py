from game.othello import BLACK

WIN_SCORE = 1000000


def evaluate(game, player):
    black_score, white_score = game.score()
    if player == BLACK:
        my_score = black_score
        opponent_score = white_score
    else:
        my_score = white_score
        opponent_score = black_score

    if game.game_over():
        if my_score > opponent_score:
            return WIN_SCORE
        if my_score < opponent_score:
            return -WIN_SCORE
        return 0

    disc_score = my_score - opponent_score
    mobility_score = len(game.get_valid_moves(player)) - len(game.get_valid_moves(-player))
    corner_score = get_corner_score(game, player)
    edge_score = get_edge_score(game, player)

    return disc_score + 5 * mobility_score + 50 * corner_score + 5 * edge_score


def ordered_moves(game, moves):
    corners = get_corners(game)
    return sorted(moves, key=lambda move: (move not in corners, move[0], move[1]))


def get_corner_score(game, player):
    score = 0
    for row, col in get_corners(game):
        if game.board[row][col] == player:
            score += 1
        elif game.board[row][col] == -player:
            score -= 1
    return score


def get_edge_score(game, player):
    score = 0
    for row, col in get_edges(game):
        if game.board[row][col] == player:
            score += 1
        elif game.board[row][col] == -player:
            score -= 1
    return score


def get_corners(game):
    n = game.size
    return [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]


def get_edges(game):
    n = game.size
    edges = []

    for i in range(1, n - 1):
        edges.append((0, i))
        edges.append((n - 1, i))
        edges.append((i, 0))
        edges.append((i, n - 1))

    return edges
