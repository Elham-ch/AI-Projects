from game.othello import Othello, BLACK, WHITE


def play_game(agent_black, agent_white):
    game = Othello(6)
    player = BLACK
    while not game.game_over():
        moves = game.get_valid_moves(player)
        if moves:
            agent = agent_black if player == BLACK else agent_white
            move = agent.choose_move(game, player)
            game.make_move(player, *move)
        if player == BLACK:
            player = WHITE
        else:
            player = BLACK
    return game.score()
