from copy import deepcopy

EMPTY = 0
BLACK = 1
WHITE = -1

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class Othello:
    def __init__(self, size=6):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        m = size // 2
        self.board[m - 1][m - 1] = WHITE
        self.board[m][m] = WHITE
        self.board[m - 1][m] = BLACK
        self.board[m][m - 1] = BLACK

    def copy(self):
        g = Othello(self.size)
        g.board = deepcopy(self.board)
        return g

    def inside(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def valid_move(self, player, row, col):
        if self.board[row][col] != EMPTY:
            return False
        opp = -player
        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            seen = False
            while self.inside(r, c) and self.board[r][c] == opp:
                seen = True
                r += dr
                c += dc
            if seen and self.inside(r, c) and self.board[r][c] == player:
                return True
        return False

    def get_valid_moves(self, player):
        return [(r, c) for r in range(self.size) for c in range(self.size)
                if self.valid_move(player, r, c)]

    def make_move(self, player, row, col):
        if not self.valid_move(player, row, col):
            return False  # reject move

        self.board[row][col] = player
        opp = -player

        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            captured = []

            while self.inside(r, c) and self.board[r][c] == opp:
                captured.append((r, c))
                r += dr
                c += dc

            if captured and self.inside(r, c) and self.board[r][c] == player:
                for rr, cc in captured:
                    self.board[rr][cc] = player

        return True

    def game_over(self):
        return not self.get_valid_moves(BLACK) and not self.get_valid_moves(WHITE)

    def score(self):
        b = sum(cell == BLACK for row in self.board for cell in row)
        w = sum(cell == WHITE for row in self.board for cell in row)
        return b, w
