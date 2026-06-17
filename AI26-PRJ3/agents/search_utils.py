from game.othello import BLACK, EMPTY

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
    mobility_score = get_mobility_score(game, player)
    corner_score = get_corner_score(game, player)
    corner_danger_score = get_corner_danger_score(game, player)
    edge_score = get_edge_score(game, player)
    edge_danger_score = get_edge_danger_score(game, player)
    disc_weight = get_disc_weight(game, black_score + white_score)

    return (
        disc_weight * disc_score
        + mobility_score
        + 35 * corner_score
        + 2 * edge_score
        - 8 * corner_danger_score
        - 2 * edge_danger_score
    )


def ordered_moves(game, moves):
    corners = set(get_corners(game))
    edges = set(get_edges(game))
    edge_danger_squares = set(get_edge_danger_squares(game))
    corner_danger_squares = get_open_corner_danger_squares(game)

    return sorted(
        moves,
        key=lambda move: (
            get_move_priority(
                move, corners, edges, edge_danger_squares, corner_danger_squares
            ),
            move[0],
            move[1],
        ),
    )


def get_move_priority(move, corners, edges, edge_danger_squares, corner_danger_squares):
    if move in corners:
        return 0
    if move in corner_danger_squares:
        return 4
    if move in edges:
        return 1
    if move in edge_danger_squares:
        return 3
    return 2


def get_disc_weight(game, occupied):
    phase = occupied / (game.size * game.size)
    if phase < 0.35:
        return 0
    if phase < 0.75:
        return 1
    return 4


def get_mobility_score(game, player):
    my_moves = len(game.get_valid_moves(player))
    opponent_moves = len(game.get_valid_moves(-player))
    total_moves = my_moves + opponent_moves

    if total_moves == 0:
        return 0
    return 100 * (my_moves - opponent_moves) / total_moves


def get_corner_score(game, player):
    score = 0
    for row, col in get_corners(game):
        if game.board[row][col] == player:
            score += 1
        elif game.board[row][col] == -player:
            score -= 1
    return score


def get_corner_danger_score(game, player):
    if game.size < 3:
        return 0

    score = 0
    for corner, squares in get_corner_danger_squares(game):
        row, col = corner
        if game.board[row][col] != EMPTY:
            continue

        for square_row, square_col in squares:
            if game.board[square_row][square_col] == player:
                score += 1
            elif game.board[square_row][square_col] == -player:
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


def get_edge_danger_score(game, player):
    score = 0
    for row, col in get_edge_danger_squares(game):
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


def get_edge_danger_squares(game):
    n = game.size
    if n < 5:
        return []

    corner_danger_squares = set()
    for _, squares in get_corner_danger_squares(game):
        corner_danger_squares.update(squares)

    squares = set()
    for i in range(1, n - 1):
        squares.add((1, i))
        squares.add((n - 2, i))
        squares.add((i, 1))
        squares.add((i, n - 2))

    return sorted(squares - corner_danger_squares)


def get_open_corner_danger_squares(game):
    danger_squares = set()
    for corner, squares in get_corner_danger_squares(game):
        row, col = corner
        if game.board[row][col] == EMPTY:
            danger_squares.update(squares)
    return danger_squares


def get_corner_danger_squares(game):
    n = game.size
    return [
        ((0, 0), [(0, 1), (1, 0), (1, 1)]),
        ((0, n - 1), [(0, n - 2), (1, n - 1), (1, n - 2)]),
        ((n - 1, 0), [(n - 2, 0), (n - 1, 1), (n - 2, 1)]),
        (
            (n - 1, n - 1),
            [(n - 2, n - 1), (n - 1, n - 2), (n - 2, n - 2)],
        ),
    ]
