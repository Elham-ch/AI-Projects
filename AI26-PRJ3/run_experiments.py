import csv
import random
import time
from pathlib import Path

from agents.alphabeta_agent import AlphaBetaAgent
from agents.greedy_agent import GreedyAgent
from agents.minimax_agent import MinimaxAgent
from agents.random_agent import RandomAgent
from game.othello import BLACK, WHITE, Othello

BOARD_SIZE = 6
GAMES = 20
SEED = 37
OPPONENTS = ["random", "greedy"]
MINIMAX_DEPTHS = [2, 3, 4]
ALPHABETA_DEPTHS = [2, 3, 4]
CSV_PATH = Path(__file__).with_name("experiment_results.csv")


def build_agent(kind, depth=None):
    if kind == "random":
        return RandomAgent()
    if kind == "greedy":
        return GreedyAgent()
    if kind == "minimax":
        return MinimaxAgent(depth=depth)
    if kind == "alphabeta":
        return AlphaBetaAgent(depth=depth)
    raise ValueError(f"Unknown agent: {kind}")


def play_game(search_kind, depth, opponent_kind, search_color):
    search_agent = build_agent(search_kind, depth)
    opponent_agent = build_agent(opponent_kind)

    if search_color == BLACK:
        black_agent = search_agent
        white_agent = opponent_agent
    else:
        black_agent = opponent_agent
        white_agent = search_agent

    game = Othello(BOARD_SIZE)
    player = BLACK
    move_times = []
    node_counts = []

    while not game.game_over():
        moves = game.get_valid_moves(player)
        if moves:
            agent = black_agent if player == BLACK else white_agent

            start = time.perf_counter()
            move = agent.choose_move(game, player)
            elapsed = time.perf_counter() - start

            if move not in moves:
                raise ValueError(f"{agent.__class__.__name__} returned illegal move {move}")

            if agent is search_agent:
                move_times.append(elapsed)
                node_counts.append(search_agent.nodes_searched)

            game.make_move(player, *move)

        player = WHITE if player == BLACK else BLACK

    black_score, white_score = game.score()
    if search_color == BLACK:
        score_diff = black_score - white_score
    else:
        score_diff = white_score - black_score

    return {
        "win": score_diff > 0,
        "loss": score_diff < 0,
        "draw": score_diff == 0,
        "score_diff": score_diff,
        "move_time": average(move_times),
        "nodes": average(node_counts),
    }


def run_matchup(agent_kind, depth, opponent_kind):
    colors = [BLACK] * (GAMES // 2) + [WHITE] * (GAMES // 2)
    if len(colors) < GAMES:
        colors.append(BLACK)

    start = time.perf_counter()
    games = [play_game(agent_kind, depth, opponent_kind, color) for color in colors]
    runtime = time.perf_counter() - start

    wins = sum(game["win"] for game in games)
    losses = sum(game["loss"] for game in games)
    draws = sum(game["draw"] for game in games)

    return {
        "agent": agent_kind,
        "depth": depth,
        "opponent": opponent_kind,
        "games": GAMES,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": wins / GAMES,
        "avg_score_diff": average([game["score_diff"] for game in games]),
        "avg_move_time": average([game["move_time"] for game in games]),
        "avg_nodes": average([game["nodes"] for game in games]),
        "runtime": runtime,
    }


def run_all():
    print()
    print("Running experiments...")
    print(f"board={BOARD_SIZE}x{BOARD_SIZE}, games={GAMES}, seed={SEED}")
    print()

    rows = []
    for opponent in OPPONENTS:
        for depth in MINIMAX_DEPTHS:
            row = run_matchup("minimax", depth, opponent)
            rows.append(row)
            print_experiment_result(row)
        for depth in ALPHABETA_DEPTHS:
            row = run_matchup("alphabeta", depth, opponent)
            rows.append(row)
            print_experiment_result(row)
    return rows


def average(values):
    return sum(values) / len(values) if values else 0


def print_results(rows):
    print()
    print("Othello experiment results")
    print(f"board={BOARD_SIZE}x{BOARD_SIZE}, games={GAMES}, seed={SEED}")
    print()

    for opponent in OPPONENTS:
        print(f"vs {opponent}")
        opponent_rows = [row for row in rows if row["opponent"] == opponent]
        print_table(opponent_rows)
        print()

    print("Alpha-Beta compared to Minimax")
    print_comparison_table(rows)
    print()
    print(f"CSV saved to: {CSV_PATH}")


def print_experiment_result(row):
    print(
        f"{row['agent']} depth {row['depth']} vs {row['opponent']}: "
        f"{row['wins']}-{row['losses']}-{row['draws']} "
        f"({100 * row['win_rate']:.0f}%), "
        f"diff={row['avg_score_diff']:.2f}, "
        f"move={1000 * row['avg_move_time']:.2f}ms, "
        f"nodes={row['avg_nodes']:.1f}, "
        f"runtime={row['runtime']:.2f}s",
        flush=True,
    )


def print_table(rows):
    headers = ["agent", "depth", "W-L-D", "win%", "diff", "move ms", "nodes", "runtime"]
    table = [headers]

    for row in rows:
        table.append([
            row["agent"],
            str(row["depth"]),
            f"{row['wins']}-{row['losses']}-{row['draws']}",
            f"{100 * row['win_rate']:.0f}%",
            f"{row['avg_score_diff']:.2f}",
            f"{1000 * row['avg_move_time']:.2f}",
            f"{row['avg_nodes']:.1f}",
            f"{row['runtime']:.2f}s",
        ])

    widths = [max(len(line[col]) for line in table) for col in range(len(headers))]
    separator = "-+-".join("-" * width for width in widths)

    print(format_row(table[0], widths))
    print(separator)
    for row in table[1:]:
        print(format_row(row, widths))


def format_row(row, widths):
    return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))


def print_comparison_table(rows):
    table = [["opponent", "depth", "AB W-L-D", "AB win%", "AB diff", "node speedup", "time speedup"]]

    for opponent in OPPONENTS:
        for depth in MINIMAX_DEPTHS:
            minimax = find_row(rows, "minimax", depth, opponent)
            alphabeta = find_row(rows, "alphabeta", depth, opponent)
            node_speedup = divide(minimax["avg_nodes"], alphabeta["avg_nodes"])
            time_speedup = divide(minimax["avg_move_time"], alphabeta["avg_move_time"])
            table.append([
                opponent,
                str(depth),
                f"{alphabeta['wins']}-{alphabeta['losses']}-{alphabeta['draws']}",
                f"{100 * alphabeta['win_rate']:.0f}%",
                f"{alphabeta['avg_score_diff']:.2f}",
                f"{node_speedup:.2f}x",
                f"{time_speedup:.2f}x",
            ])

    widths = [max(len(line[col]) for line in table) for col in range(len(table[0]))]
    separator = "-+-".join("-" * width for width in widths)

    print(format_row(table[0], widths))
    print(separator)
    for row in table[1:]:
        print(format_row(row, widths))


def divide(a, b):
    return a / b if b else 0


def find_row(rows, agent, depth, opponent):
    for row in rows:
        if row["agent"] == agent and row["depth"] == depth and row["opponent"] == opponent:
            return row
    raise ValueError(f"Missing result: {agent} depth {depth} vs {opponent}")


def write_csv(rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    random.seed(SEED)
    rows = run_all()
    write_csv(rows)
    print_results(rows)


if __name__ == "__main__":
    main()
